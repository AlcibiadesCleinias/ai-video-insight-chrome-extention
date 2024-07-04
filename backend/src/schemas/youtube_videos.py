from pydantic import BaseModel


class YoutubeVideoIn(BaseModel):
    video_id: str


class YoutubeVideoOut(YoutubeVideoIn):
    clickbait_ratio: float
    video_summary: str
    comments_summary: str