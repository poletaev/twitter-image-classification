import os

from flask import Flask
from flask_googlemaps import GoogleMaps

from google_map import google_map

def create_app(**kwargs):
    app = Flask(__name__)
    app.config.from_pyfile('../../etc/frontend_default.cfg')
    try:
        env_config = 'FRONTEND_FOR_TWEETS_SETTINGS'
        if os.getenv(env_config) is not None:
            app.config.from_envvar(env_config)
        else:
            app.logger.info("Environment variable {} was not set."
                            .format(env_config))
    except Exception as e:
        app.logger.error("Error: {}".format(e.message))

    if 'debug' in kwargs and kwargs['debug'] in (True, False):
        app.debug = kwargs['debug']

    app.register_blueprint(google_map)
    GoogleMaps(app)
    return app
