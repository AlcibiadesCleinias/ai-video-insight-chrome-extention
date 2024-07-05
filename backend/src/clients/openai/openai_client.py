import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, List

import aiohttp

from clients.openai.schemes import ChatMessage, ChatMessages, OpenAIChatChoices
from clients.ai_client import AIClientABC
from config.logger import get_app_logger

logger = get_app_logger()


class OpenAIMaxTokenExceededError(Exception):
    pass


class OpenAIInvalidRequestError(Exception):
    pass


@dataclass
class TokenRequestResponse:
    json: any
    status: int
    failed_tokens: list[str]


class OpenAIAPIClient:
    COMPLETION_MAX_LENGTH = 4097
    ERROR_MAX_TOKEN_MESSAGE = 'This model\'s maximum context'
    DEFAULT_NO_COMPLETION_CHOICE_RESPONSE = 'A?'
    DEFAULT_TOKEN_TO_BE_ROTATED_STATUSES = {401}
    DEFAULT_FORCE_MAIN_TOKEN_STATUSES = {400}
    DEFAULT_RETRY_ON_429 = 1  # Thus, totally 2 times.

    DEFAULT_CHAT_BOT_ROLE = 'assistant'
    DEFAULT_IMAGE_PROMT_PREFIX = (
        'I NEED to test how the tool works with extremely simple prompts. '
        'DO NOT add any detail, just use it AS-IS:'
    )

    class Method(Enum):
        COMPLETIONS = 'completions'
        CHAT_COMPLETIONS = 'chat/completions'
        IMAGE_GENERATION = 'images/generations'

    def __init__(
        self,
        token: Optional[str] = None,
        endpoint: str = 'https://api.openai.com/v1/',
    ):
        self.token = token
        self.endpoint = endpoint

    async def make_request(
            self,
            url,
            data,
            headers={},
            *args,
            **kwargs,
    ) -> TokenRequestResponse:
        current_token = self.token
        headers['Authorization'] = f'Bearer {current_token}'

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=url,
                json=data,
                headers=headers,
            ) as response:
                status = response.status
                _json = await response.json()
                logger.info('[TokenApiRequestPureManager] Send %s, on %s got status = %s, json = %s',
                            data, url, status, _json)

                return TokenRequestResponse(
                    status=status,
                    json=_json,
                    failed_tokens=[],
                )

    async def _make_request(self, method: Method, data: dict, try_count: int = 0):
        url = self.endpoint + method.value
        api_manager_response = await self.make_request(
            url=url, data=data, rotate_statuses=self.DEFAULT_TOKEN_TO_BE_ROTATED_STATUSES,
            force_main_token_statuses=self.DEFAULT_FORCE_MAIN_TOKEN_STATUSES,
        )
        response = api_manager_response.json
        status = api_manager_response.status
        logger.debug('[OpenAIClient] Got response %s with status %s', response, status)

        if status == 400 and response.get('error', {}).get('message', '').startswith(
                self.ERROR_MAX_TOKEN_MESSAGE):
            logger.warning('[OpenAIClient] Got invalid_request_error from openai, raise related exception.')
            raise OpenAIMaxTokenExceededError

        if status == 429 and try_count <= self.DEFAULT_RETRY_ON_429:
            logger.warning(f'[OpenAIClient] Got 429 status, {try_count=}, retry 1 more time if possible...')
            return await self._make_request(method, data, try_count + 1)

        if status == 401:
            raise OpenAIInvalidRequestError(f'Got response from OpenAI: {response}')
        return response

    async def parse_chat_choices(self, response: OpenAIChatChoices) -> str:
        choices = response.choices
        if not choices:
            logger.warning('No choices from OpenAI, send nothing...')
            return self.DEFAULT_NO_COMPLETION_CHOICE_RESPONSE

        logger.debug('Choose first completion in %s & send.', response)
        return choices[0].message.content

    async def get_chat_completions(self, messages: [ChatMessage], chat_bot_goal: str) -> str:
        """
        :param messages: previous messages + new message from a user.
        :param chat_bot_goal: e.g. You are a helpful assistant.
        """
        chat_bot_goal = ChatMessage(
            role='system',
            content=chat_bot_goal,
        )
        messages = ChatMessages(root=[chat_bot_goal] + messages)
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': json.loads(messages.json()),
            'n': 1,
        }
        response = await self._make_request(self.Method.CHAT_COMPLETIONS, data)
        return await self.parse_chat_choices(OpenAIChatChoices(**response))


class OpenAIClient(AIClientABC):
    MAX_COMMENTS = 10

    def __init__(self, token):
        self.api_client = OpenAIAPIClient(token)

    async def get_video_summary_from_transcript(self, title, transcript: str) -> str:
        content = f"Video with title {title} consists the following transcript: {transcript}"
        return await self.api_client.get_chat_completions(
            [ChatMessage(role='user', content=content)],
            chat_bot_goal=(
                'Your task is to provide a one-sentence summary of the video content presented. '
                'Ensure the summary captures the core message and key details effectively'
            )
        )

    async def get_comments_summary(self, title: str, comments: List[Tuple[str, str]]) -> str:
        comments_text = [
            f'{idx}. From: {comment[0]}. Comment: {comment[1]}\n' for idx, comment in enumerate(comments)
            if idx < self.MAX_COMMENTS
        ]
        content = (f"Create summary to the following comments of the video title {title}, "
                   f"Note that comments sorted in descending order (from most liked to less): {comments_text}")
        return await self.api_client.get_chat_completions(
            [ChatMessage(role='user', content=content)],
            chat_bot_goal=(
                'Your task is to provide a one-sentence summary of the video comments (in dl;dr format). '
                'Ensure the summary captures the core message and key details effectively'
            )
        )

    async def get_click_bait_ratio_with_summary(
            self, title: str, video_summary: str, likes: float, views: float, comments_total: Optional[int] = None,
    ) -> str:
        content = (
            f"Provide click-bait ratio for video with title: {title} transcript summary: "
            f"{video_summary}. Likes: {likes}. Views: {views}"
        )
        if comments_total:
            content += f". Total comments: {comments_total}"

        return await self.api_client.get_chat_completions(
            [ChatMessage(role='user', content=content)],
            chat_bot_goal=(
                'Your task is to provide a one-sentence (max 20 chars) analysis on the video click bait. '
                'Ensure the click bait analysis captures all the provided features and key details effectively. '
                "Format of the analysis should be: 'Ratio: from 0 to 100, where 100 is the most click bait'. "
                'Description: your text of summary.'
                "Short example: Ratio: 90. Low like-to-view ratio and the title doesn't match the content."
            )
        )
