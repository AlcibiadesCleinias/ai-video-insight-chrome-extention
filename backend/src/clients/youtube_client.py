import re
from dataclasses import dataclass
from typing import List

from pytube import YouTube

@dataclass
class YoutubeVideoInfo:
    title: str
    views: int
    likes: int

number_extract_pattern = "\\d+"


class YoutubeClient:

    def _parse_likes_number(self, yt: YouTube) -> int:
        likes_text = yt.initial_data['contents'] \
            ['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer'] \
            ['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonViewModel'] \
            ['likeButtonViewModel']['likeButtonViewModel']['toggleButtonViewModel']['toggleButtonViewModel'] \
            ['defaultButtonViewModel']['buttonViewModel']['accessibilityText']
        likes_number = re.findall(number_extract_pattern, likes_text)
        return int(''.join(likes_number))

    async def get_video_info(self, video_id: str) -> YoutubeVideoInfo:
        yt = YouTube(f'https://youtu.be/{video_id}')
        try:
            likes_number = self._parse_likes_number(yt)
        except Exception as e:
            likes_number = -1

        return YoutubeVideoInfo(
            title=yt.title,
            views=yt.views,
            likes=likes_number,
        )

    def get_video_comments(self, video_id: str) -> List[dict]:
        pass

    def get_video_transcript(self, video_id: str) -> str:
        pass