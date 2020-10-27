import logging
import logging.config
import os

from aircraft.plan import Plan

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
            'level': 'WARNING',
            'propagate': False
        },
        'aircraft': {
            'handlers': ['default'],
            'level': os.environ.get("AIRCRAFT_LOGLEVEL", 'WARN'),
            'propagate': False
        },
    }
}
logging.config.dictConfig(LOGGING_CONFIG)

__all__ = (
    "Plan",
)
