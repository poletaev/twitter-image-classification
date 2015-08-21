# Broker settings.
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('classify_tweets.tasks',
                  'classify_tweets.db')

# Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'rpc://'

# CELERY_ANNOTATIONS = {'tweets.send_tweet': {'rate_limit': '10/s'}}
# CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']

CELERYD_CONCURRENCY = 1

MODEL_DEF_FILE = 'models/bvlc_reference_caffenet/deploy.prototxt'
PRETRAINED_MODEL_FILE = 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'
MEAN_FILE = 'models/bvlc_reference_caffenet/ilsvrc_2012_mean.npy'
CLASS_LABELS_FILE = 'models/bvlc_reference_caffenet/synset_words.txt'
BET_FILE = 'models/bvlc_reference_caffenet/imagenet.bet.pickle'
GPU_MODE = False
TMP_DIR = '/tmp/d'
