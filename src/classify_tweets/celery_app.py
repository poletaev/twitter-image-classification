from __future__ import absolute_import

from celery import Celery

app = Celery('tweets')

app.config_from_object('classify_tweets.worker_default')

# Optional configuration
app.conf.update(
    CELERY_IGNORE_RESULT=True,
)

if __name__ == '__main__':
    app.start()
