from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1: str = '/api/v1'
    LOG_LEVEL: str = 'INFO'
    LOGGER_NAME: str = 'app_logger'

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    OPENAI_TOKEN: str

    API_CACHE_TTL: int = 60 * 10

    class Config:
        case_sensitive = True


settings = Settings()


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s | %(asctime)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',  # todo: default?
        },
    },
    'loggers': {
        'root': {
            'handlers': ['default'],
            'level': settings.LOG_LEVEL,
        },
        settings.LOGGER_NAME: {
            'handlers': ['default'],
            'level': settings.LOG_LEVEL,
        },
    },
}
