from typing import List


class YoutubeClient:
    async def get_video_nfo(self, video_id: str) -> dict:
        pass

    def get_video_comments(self, video_id: str) -> List[dict]:
        pass

    def get_video_transcript(self, video_id: str) -> str:
        pass