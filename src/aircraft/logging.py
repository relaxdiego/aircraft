import logging
import logging.config


def configure_logging():
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "simple": {
                "format": '%(asctime)s  %(name)-30s %(levelname)-7s %(message)s'
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            }
        },

        "loggers": {
            "aircraft": {
                "propagate": "no",
                "handlers": [
                    "console"
                ]
            }
        }
    })
