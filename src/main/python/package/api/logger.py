import logging
import logging.config
import logging.handlers
import pathlib

LOG_LEVEL = logging.DEBUG

LOG_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "log" / "compare.log"
TIMESTAMP_STR = "%d/%m %H:%M:%S"


roll_log = LOG_PATH.is_file()
# log dir
dir_path = LOG_PATH.parent
if not dir_path.is_dir():
    dir_path.mkdir(parents=True)

config = {
    "disable_existing_loggers": False,
    "version": 1,
    "formatters": {
        # "file": {
        #     "format": "%(asctime)s\t%(levelname)s\t%(module)s\t%(funcName)s\t%(message)s",
        #     "datefmt": TIMESTAMP_STR,
        # },
        "stream": {
            "format": "%(name)s\t%(levelname)s\t%(message)s"
        },
    },
    "handlers": {
        # "file": {
        #     "formatter": "file",
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "filename": LOG_PATH,
        #     "mode": "a",
        #     "maxBytes": 10000000,
        #     "backupCount": 5
        # },
        "stream": {
            'formatter': 'stream',
            'class': 'logging.StreamHandler',
        },
    },
    "loggers": {
        "": {
            "handlers": ["stream"],
            "level": LOG_LEVEL
        },
    },
}

logging.config.dictConfig(config)
# if roll_log:
#     # fait tourner les fichiers logs
#     rotating_handler = \
#     [h for h in logging.getLogger().handlers if isinstance(h, logging.handlers.RotatingFileHandler)][0]
#     rotating_handler.doRollover()
