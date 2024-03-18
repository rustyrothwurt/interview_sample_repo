from datetime import date


def get_app_logging_config(config):
    """

    Args:
        config:  passed in flask app config (app.cofig)

    Returns:
        dict: log config object as dict (use dictConfig from logging to configure)
    """
    LOG_FILE = config.get("LOG_FILE", "app_{0}.log".format((date.today()).strftime("%Y-%m-%d")))
    LOG_LEVEL = config.get("LOG_LEVEL", "INFO")
    LOG_CONFIG = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: {%(pathname)s:%(funcName)s:%(lineno)d}: %(message)s',
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'default': {
                'level': LOG_LEVEL,
                'formatter': 'default',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOG_FILE,
                'maxBytes': 50000,
                'backupCount': 3
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': LOG_LEVEL,
                'formatter': 'default',
            }},
        'root': {
            'handlers': ["console"],
            'level': LOG_LEVEL,
        },
    }
    return LOG_CONFIG