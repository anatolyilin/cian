import logging

from .configuration import app_config

_FALLBACK_LOGGING_LEVEL = "INFO"


def get_logger() -> logging:
    logger = logging.getLogger(app_config.get_nested("app.name"))
    logging_level = app_config.get_nested("logging.level", _FALLBACK_LOGGING_LEVEL)
    print(f"Setting logging level to {logging_level}")
    logger.setLevel(logging_level)
    add_format(logger, log_format=app_config.get_nested("logging.format"))
    return logger


def add_format(logger, log_format=None):
    if len(logger.handlers) == 0:
        stream_handler = logging.StreamHandler()
        logger.addHandler(stream_handler)
    else:
        stream_handler = logger.handlers[0]

    if log_format is None:
        log_format = "[%(asctime)s] - %(levelname)s - %(module)s - %(message)s"
    stream_handler.setFormatter(logging.Formatter(log_format))
