from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from classify_tweets import models

import argparse
import logging

logging.basicConfig()
logger = logging.getLogger('create_db')

def init_db(engine=None):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    # import large_attachment_handling.models
    models.Base.metadata.create_all(bind=engine)


def drop_db(engine=None):
    models.Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    # CREATE USER 'test'@'localhost' IDENTIFIED BY 'password';
    # CREATE DATABASE dev;
    # GRANT ALL PRIVILEGES ON dev.* TO 'test'@'localhost' WITH GRANT OPTION;
    # FLUSH PRIVILEGES;

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    mysql_group = parser.add_argument_group()
    mysql_group.add_argument("-u", "--user",
                             help="User for login.",
                             default="test")
    mysql_group.add_argument("-p", "--password",
                             help="Password to use when connecting to server.",
                             default="password")
    mysql_group.add_argument("-H", "--host",
                             help="Hostname used when connecting.",
                             default="localhost")
    mysql_group.add_argument("-P", "--port",
                             help="Port number to use for connection",
                             type=int, default=3306,)
    mysql_group.add_argument("-d", "--database",
                             help="Database to use",
                             default="dev")

    args = parser.parse_args()

    if args.quiet:
        logger.setLevel(logging.WARNING)
    elif args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    engine = create_engine("mysql://{}:{}@{}:{}/{}?charset=utf8"
                           .format(args.user, args.password, args.host,
                                   args.port, args.database),
                           convert_unicode=True,
                           pool_recycle=3600)

    session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))

    session.configure(bind=engine)
    init_db(engine)
