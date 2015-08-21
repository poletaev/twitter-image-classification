from __future__ import absolute_import

import logging
import os
from celery import Celery

app = Celery('tweets')

logger = logging.getLogger(__name__)

app.config_from_object('classify_tweets.worker_default')

try:
    env_config = 'CLASSIFY_TWEETS_SETTINGS'
    if os.getenv(env_config) is not None:
        app.config_from_envvar(env_config)
    else:
        logger.warning("Environment variable {} was not set."
                        .format(env_config))
except Exception as e:
    logger.exception("Error: {}".format(e.message))

# Optional configuration
app.conf.update(
    CELERY_IGNORE_RESULT=True,
)

if __name__ == '__main__':
    app.start()
