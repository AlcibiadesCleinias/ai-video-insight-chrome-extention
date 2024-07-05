from logging.config import dictConfig
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis
from starlette.middleware.cors import CORSMiddleware

from api.api import api_router
from config.logger import get_app_logger
from config.settings import settings, LOGGING


dictConfig(LOGGING)
logger = get_app_logger()


app = FastAPI(
    title='AI Video Insight API Endpoint',
    openapi_url=f'{settings.API_V1}/openapi.json',
)

app.include_router(api_router, prefix=settings.API_V1)

app.add_middleware(
    CORSMiddleware,
    # TODO: change to settings.ORIGINS
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup():
    redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, encoding='utf8', decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
