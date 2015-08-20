# Broker settings.
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('classify_tweets.tasks', 'classify_tweets.db' )

# Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'rpc://'

# CELERY_ANNOTATIONS = {'tweets.send_tweet': {'rate_limit': '10/s'}}
# CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']


CELERYD_CONCURRENCY = 1