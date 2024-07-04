import re
from dataclasses import dataclass
from typing import List
from itertools import islice

from pytube import YouTube
from youtube_comment_downloader import SORT_BY_POPULAR, YoutubeCommentDownloader

@dataclass
class YoutubeVideoInfo:
    title: str
    views: int
    likes: int

@dataclass
class YoutubeVideoComment:
    author: str
    text: str
    votes: int

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

    async def get_video_comments(self, video_id: str, max_comments: int=5) -> List[YoutubeVideoComment]:
        downloader = YoutubeCommentDownloader()
        comments = downloader.get_comments_from_url(
            f'https://youtu.be//{video_id}', sort_by=SORT_BY_POPULAR)
        serialized_comments = []
        for comment in islice(comments, max_comments):
            serialized_comments.append(
                YoutubeVideoComment(
                    author=comment['author'],
                    text=comment['text'],
                    votes=comment['votes'],
                )
            )
        return serialized_comments

    def get_video_transcript(self, video_id: str) -> str:
        pass