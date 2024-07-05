
from fastapi import APIRouter
from fastapi_cache.decorator import cache

import schemas
from api.deps import ai_video_insight_client

from clients.youtube_scrapper_client import YoutubeScrapperClient
from config.logger import get_app_logger
from config.settings import settings

logger = get_app_logger()
router = APIRouter()

# TODO: add caching {fetched data from youtube, ai insights responses}.


@router.get(
    '/youtube-videos/',
    description=(
        'Get short analysis of youtube video.'
    ),
    response_model=schemas.YoutubeVideoOut,
)
@cache(expire=settings.API_CACHE_TTL)
async def get_youtube_video_insights(video_id: str):
    logger.info(f'Fetching data for video: {video_id}')
    # TODO: consists of blocked code.
    # TODO: it could be parallelized, but check above (min time-cons solution: to separate rpc services).
    youtube_client = YoutubeScrapperClient()
    video_data = await youtube_client.get_video_data(video_id)

    logger.info(f'Get model inferences for video: {video_id}')
    insights = await ai_video_insight_client.get_insights(
        title=video_data.info.title,
        transcript=video_data.transcript,
        comments=[(comment.author, comment.text) for comment in video_data.comments],
        likes=video_data.info.likes,
        views=video_data.info.views,
    )

    return schemas.YoutubeVideoOut.construct(
        clickbait_ratio_summary=insights.clickbait_ratio_summary,
        video_summary=insights.video_summary,
        comments_summary=insights.comments_summary,
    )
