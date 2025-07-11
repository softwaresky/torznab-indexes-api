def get_logging_config():
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(levelname)s: [%(name)s:%(funcName)s:%(lineno)s] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
        },
        "loggers": {
            "root": {
                "handlers": ["console"],
                "propagate": False,
                "level": "INFO",
            },
            # "uvicorn": {
            #     "handlers": ["console"],
            #     "propagate": False,
            #     "level": "DEBUG",
            # },
        },
    }
