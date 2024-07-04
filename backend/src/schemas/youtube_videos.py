from pydantic import BaseModel


class YoutubeVideoIn(BaseModel):
    video_id: str


class YoutubeVideoOut(BaseModel):
    clickbait_ratio_summary: str
    video_summary: str
    comments_summary: str