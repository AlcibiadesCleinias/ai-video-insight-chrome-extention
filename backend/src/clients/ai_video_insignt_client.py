import asyncio
from typing import List, Tuple

import schemas
from clients.ai_client import AIClientABC
from config.logger import get_app_logger

logger = get_app_logger()


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
            self, transcript: str, comments: List[Tuple[str, str]], likes: float, views: float
    ) -> schemas.YoutubeVideoOut:

        # TODO: use different models, and use the first answer available with e.g. asyncio.FIRST_COMPLETED

        try:
            gathered_tasks = await asyncio.gather(
                self.ai_client.get_comments_summary(comments),
                self.ai_client.get_video_summary_from_transcript(transcript),
            )
            video_summary = gathered_tasks[1]
            comments_summary = gathered_tasks[0]

            clickbait_ratio_summary = await self.ai_client.get_click_bait_ratio(video_summary, likes, views)
        except Exception as e:
            logger.error(f"Failed to get insights: {e}, return simple answer...")
            video_summary = transcript[:100]
            comments_summary = comments[0][1]
            clickbait_ratio_summary = "0.5"


        # Lest calculate click bate ratio with AI, but supplying summaries instead of raw data.

        return schemas.YoutubeVideoOut(
            video_summary=video_summary,
            comments_summary=comments_summary,
            clickbait_ratio=clickbait_ratio_summary,
        )

