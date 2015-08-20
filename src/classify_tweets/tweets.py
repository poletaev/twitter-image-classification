from __future__ import absolute_import, print_function

import argparse
import ConfigParser
import json
import logging
import os
import time

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import tasks

logging.basicConfig()
logger = logging.getLogger('tweets_producer')


class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_status(self, status):
        """
        Callback when post is received ok
        """
        if 'media' in status.entities:
            message = {
                'coordinates': status.coordinates,
                'media': status.entities['media'],
                'text': status.text,
                'time': int(time.time())

            }
            logger.info(message['media'])
            tasks.send_tweet.apply_async((json.dumps(message),),
                                   queue='russir')

    def on_error(self, status):
        logger.error("Got error: {}".format(status))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("config", nargs='?', type=str,
                        help="Path to config file",
                        default="../../etc/tweets_producer_default.cfg")

    args = parser.parse_args()

    if args.quiet:
        logger.setLevel(logging.WARNING)
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if not os.path.exists(args.config):
        parser.exit(1,
                    "Configuration file {} doesn't exist".format(args.config))

    config = ConfigParser.ConfigParser()
    try:
        config.read(args.config)
    except ConfigParser.ParsingError as e:
        parser.exit(1, e.message)

    l = StdOutListener()
    auth = OAuthHandler(config.get('twitter', 'consumer_key'),
                        config.get('twitter', 'consumer_secret'))
    auth.set_access_token(config.get('twitter', 'access_token'),
                          config.get('twitter', 'access_token_secret'))

    stream = Stream(auth, l)
    stream.filter(locations=[-180, -90, 180, 90])
