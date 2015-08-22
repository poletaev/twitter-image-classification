#from __future__ import absolute_import

import sys

from celery.utils.log import get_task_logger
from celery import task
from celery import Task

from sqlalchemy.exc import IntegrityError, ProgrammingError

from db import db_session
from models import Tweets
from caffe_classifier.caffe_classifier import ImagenetClassifier, FailToClassify

logger = get_task_logger(__name__)


class SqlAlchemyDbTask(Task):
    """
    A base Task class that caches a database connection
    """
    abstract = True
    _clf = None

    def __init__(self):
        result = self.app.conf.get('MODEL_DEF_FILE')
        logger.info(result)

    @property
    def clf(self):
        if self._clf is None:
            result = self.app.conf.get('MODEL_DEF_FILE')
            logger.info(result)
            self._clf = ImagenetClassifier(
                prototxt=self.app.conf.get('MODEL_DEF_FILE'),
                caffemodel=self.app.conf.get('PRETRAINED_MODEL_FILE'),
                mean_file=self.app.conf.get('MEAN_FILE'),
                class_labels=self.app.conf.get('CLASS_LABELS_FILE'),
                bet_file=self.app.conf.get('BET_FILE'),
                gpu=self.app.conf.get('GPU_MODE'),
                tmp_dir=self.app.conf.get('TMP_DIR'))
        return self._clf

    def after_return(self, *args, **kwargs):
        db_session.remove()


@task(name='tasks.send_tweet', base=SqlAlchemyDbTask, serializer='json')
def send_tweet(data):
    logger.info("send_tweet function")
    try:
        result = send_tweet.clf.hedging_top_n_classes(
            data['media'][0]['media_url_https'],
            top_n=5)
        logger.info(result)
    except FailToClassify as e:
        logger.exception(e.message)
        return

    classes = u'<ul>' + \
              reduce(lambda x, y: x + y,
                     map(lambda x: '<li>' + x + '</li>',
                         result[0])) + \
              u'</ul>'

    try:
        t = Tweets(text=data['text'],
                   photo_url=data['media'][0]['media_url_https'],
                   date=data['time'],
                   longitude=data['coordinates'][0],
                   latitude=data['coordinates'][1],
                   classes=classes
                   )
        db_session.add(t)
        db_session.commit()

    except IntegrityError as e:
        db_session.rollback()
        logger.exception("IntegrityError: {}".format(e.message))
    except:
        db_session.rollback()
        e = sys.exc_info()[0]
        logger.exception("Error: %s" % e)
