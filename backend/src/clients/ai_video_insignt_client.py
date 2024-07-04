import asyncio
from typing import List, Tuple

import schemas
from clients.ai_client import AIClientABC
from config.logger import get_app_logger

logger = get_app_logger()

COMMENTS_SUMMARY_NOT_AVAILABLE_TXT = "No comments available"
VIDEO_SUMMARY_NOT_AVAILABLE_TXT = "Summary of the video is not available right now, retry latter"
CLICKBAIT_RATIO_NOT_AVAILABLE_TXT = "Ratio is not available right now, retry latter"


class AIVideoInsightClient:
    """The core client of the project, it should evaluate different strategies on how to get insights from the video
     {first ready, gridy within 5 seconds and etc}

    Currently, in case of any fail it returns title + description [:MAX_LENGTH_SIMPLE_SUMMARY], first comment, and 0.5 clickbait ratio.
    """
    MAX_LENGTH_SIMPLE_SUMMARY = 100

    # ToDo: support more clients
    def __init__(self, ai_client: AIClientABC):
        self.ai_client = ai_client

    async def get_insights(
            self, title: str, transcript: str, comments: List[Tuple[str, str]], likes: float, views: float
    ) -> schemas.YoutubeVideoOut:

        # TODO: use different models, and use the first answer available with e.g. asyncio.FIRST_COMPLETED
        try:
            gathered_tasks = await asyncio.gather(
                self.ai_client.get_comments_summary(title, comments),
                self.ai_client.get_video_summary_from_transcript(title, transcript),
            )
            video_summary = gathered_tasks[1] if len(transcript) > 0 else VIDEO_SUMMARY_NOT_AVAILABLE_TXT
            comments_summary = gathered_tasks[0] if len(comments) > 0 else COMMENTS_SUMMARY_NOT_AVAILABLE_TXT
            logger.info(f'Got comments_summary: {comments_summary}, video_summary_from_transcript: {video_summary}')

            if len(transcript) > 0:
                clickbait_ratio_summary = await self.ai_client.get_click_bait_ratio_with_summary(
                    title=title,
                    video_summary=video_summary,
                    likes=likes,
                    views=views,
                )
            else:
                clickbait_ratio_summary = CLICKBAIT_RATIO_NOT_AVAILABLE_TXT
        except Exception as e:
            logger.error(f"Failed to get insights: {e}, return simple answer...")
            video_summary = transcript[:100]
            comments_summary = comments[0][1] if len(comments) > 0 else COMMENTS_SUMMARY_NOT_AVAILABLE_TXT
            clickbait_ratio_summary = CLICKBAIT_RATIO_NOT_AVAILABLE_TXT

        return schemas.YoutubeVideoOut(
            clickbait_ratio_summary=clickbait_ratio_summary,
            video_summary=video_summary,
            comments_summary=comments_summary,
        )

