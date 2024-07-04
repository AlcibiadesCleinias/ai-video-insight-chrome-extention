from abc import ABC
from typing import Tuple, List, Optional


class AIClientABC(ABC):
    async def get_video_summary_from_transcript(self, title, text: str) -> str:
        return NotImplemented

    async def get_comments_summary(self, title, comments: List[Tuple[str, str]]) -> str:
        """Get 1 line comment summary of the ordered comments."""
        return NotImplemented

    async def get_click_bait_ratio_with_summary(
            self, title: str, video_summary: str, likes: float, views: float, comments_total: Optional[int]=None) -> str:
        return NotImplemented