import logging
import logging.config

from pydantic import BaseSettings

from aircraft.plan import Plan


class Settings(BaseSettings):

    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_prefix = 'AIRCRAFT_'


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        # root logger
        '': {
            'handlers': ['default'],
            'level': Settings().LOG_LEVEL,
            'propagate': False
        },
        'aircraft': {
            'handlers': ['default'],
            'level': Settings().LOG_LEVEL,
            'propagate': False
        },
    }
}
logging.config.dictConfig(LOGGING_CONFIG)

__all__ = (
    "Plan",
)
