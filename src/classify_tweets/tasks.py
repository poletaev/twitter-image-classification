#from __future__ import absolute_import

import datetime
import json
import sys

from celery.utils.log import get_task_logger
from celery import task
from celery import Task

from sqlalchemy.exc import IntegrityError, ProgrammingError

from db import db_session
from models import Tweets

logger = get_task_logger(__name__)


class SqlAlchemyDbTask(Task):
    """
    A base Task class that caches a database connection
    """
    abstract = True

    def after_return(self, *args, **kwargs):
        db_session.remove()


@task(name='tasks.send_tweet', base=SqlAlchemyDbTask, serializer='json')
def send_tweet(data):
    logger.info("send_tweet function")
    logger.info(data)
    try:
        t = Tweets(data['text'],
                   data['media'][0]['media_url_https'],
                   data['time'])
        db_session.add(t)
        db_session.commit()

    except IntegrityError as e:
        db_session.rollback()
        logger.debug("IntegrityError: {}".format(e.message))
    except:
        db_session.rollback()
        e = sys.exc_info()[0]
        logger.error("Error: %s" % e)
