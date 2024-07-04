from abc import ABC


class AIClientABC(ABC):
    async def get_video_summary_from_transcript(self, text: str) -> str:
        return NotImplemented

    async def get_comments_summary(self, comments: list[(str, str)]) -> str:
        """Get 1 line comment summary of the ordered comments."""
        return NotImplemented

    async def get_click_bait_ratio(self, video_summary: str, likes: float, views: float) -> float:
        return NotImplemented