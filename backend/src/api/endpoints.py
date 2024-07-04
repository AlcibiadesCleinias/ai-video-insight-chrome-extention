from fastapi import APIRouter

import schemas

from clients.youtube_scrapper_client import YoutubeScrapperClient
from config.logger import get_app_logger

logger = get_app_logger()
router = APIRouter()

# TODO: add caching {fetched data from youtube, ai insights responses}.
@router.post(
    '/youtube',
    description=(
        'Get short analysis of youtube video.'
    ),
    response_model=schemas.YoutubeVideoOut,
)
async def get_youtube_video_insights(youtube_video_in: schemas.YoutubeVideoIn):
    logger.info(f'Fetching data for video: {youtube_video_in.video_id}')
    # TODO: consists of blocked code.
    # TODO: it could be parallelized, but check above (min time-cons solution: to separate rpc services).
    youtube_client = YoutubeScrapperClient()
    video_data = await youtube_client.get_video_data(youtube_video_in.video_id)

    logger.info(f'Get model inferences for video: {youtube_video_in.video_id}')

    # await ai_video_insight_client.get_insights()
    return schemas.YoutubeVideoOut.construct(
        clickbait_ratio="",
        video_summary="",
        comments_summary="",
    )
