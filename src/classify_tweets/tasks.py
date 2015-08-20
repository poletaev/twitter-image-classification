from __future__ import absolute_import

from celery.utils.log import get_task_logger
from celery import task

logger = get_task_logger(__name__)

@task(name='tasks.send_tweet')
def send_tweet(tweet):
    logger.info("send_tweet function")
    return tweet

