import re
from dataclasses import dataclass
from typing import List, Optional
from itertools import islice

from pytube import YouTube
from youtube_comment_downloader import SORT_BY_POPULAR, YoutubeCommentDownloader
from youtube_transcript_api import YouTubeTranscriptApi

from config.logger import get_app_logger

logger = get_app_logger()

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

@dataclass
class YoutubeVideoData:
    info: YoutubeVideoInfo
    comments: List[YoutubeVideoComment]
    transcript: Optional[str]

number_extract_pattern = "\\d+"


class YoutubeScrapperClient:
    """Client for scrapping youtube video info, comments and transcript.
    Currently, it uses sync packagges [blocking code].
    """
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

    async def get_video_transcript(self, video_id: str) -> str:
        response = YouTubeTranscriptApi.get_transcript(video_id)
        return '\n'.join([item['text'] for item in response])

    async def get_video_data(self, video_id: str) -> YoutubeVideoData:
        # No parallel coz of blocking code.
        video_info = await self.get_video_info(video_id)
        # Less reliable calls below.
        try:
            video_comments = await self.get_video_comments(video_id)
        except Exception as e:
            logger.error('Failed to fetch video comments: %s', e)
            video_comments = []
        logger.info('Fetched video comment: %s', video_comments)

        try:
            video_transcript = await self.get_video_transcript(video_id)
        except Exception as e:
            logger.error('Failed to fetch video transcript: %s', e)
            video_transcript = None
        logger.info('Fetched video transcript: %s', video_transcript)
        return YoutubeVideoData(info=video_info, comments=video_comments, transcript=video_transcript)

