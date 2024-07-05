from clients.ai_video_insignt_client import AIVideoInsightClient
from clients.openai.openai_client import OpenAIClient
from config.settings import settings

openai_client = OpenAIClient(settings.OPENAI_TOKEN)
ai_video_insight_client = AIVideoInsightClient(openai_client)
