from fastapi import APIRouter

import schemas

router = APIRouter()

@router.post(
    '/youtube',
    description=(
        'Get short analysis of youtube video.'
    ),
    response_model=schemas.YoutubeVideoOut,
)
async def get_youtube_video_insights(youtube_video_in: schemas.YoutubeVideoIn):
    # TODO: Check if already requested: return answer, or wait for 5 sec.
    # lock and
    # Start pipeline with video_id, return finally.

    # TODO
    return schemas.YoutubeVideoOut.construct()
