import logging
import os

from flask import Flask
from flask_googlemaps import GoogleMaps
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from google_map import google_map


def create_app(bind='development', debug=False, default_config=None,
               mysql_path=None):

    app = Flask(__name__)

    if default_config is None:
        app.config.from_pyfile('../../etc/frontend_default.cfg')
    else:
        app.config.from_object(default_config)

    try:
        env_config = 'FRONTEND_FOR_TWEETS_SETTINGS'
        if os.getenv(env_config) is not None:
            app.config.from_envvar(env_config)
        else:
            app.logger.info("Environment variable {} was not set."
                            .format(env_config))
    except Exception as e:
        app.logger.error("Error: {}".format(e.message))

    # set logger format and logging level
    logging.basicConfig(format=app.config['LOG_FORMAT'],
                        level=app.config['LOG_LEVEL'])
    app.debug_log_format = app.config['LOG_FORMAT']

    # set up database
    if mysql_path is None:
        app.engine = create_engine(app.config['SQLALCHEMY_BINDS'][bind],
                                   convert_unicode=True,
                                   pool_recycle=3600,
                                   pool_size=10)
    else:
        app.engine = create_engine(mysql_path,
                                   convert_unicode=True,
                                   pool_recycle=3600,
                                   pool_size=10)

    app.db_session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=app.engine))

    # set debug
    app.debug = debug

    app.register_blueprint(google_map)
    google_map.logger = app.logger

    GoogleMaps(app)
    return app
