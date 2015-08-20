from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tweets(Base):
    __tablename__ = 'tweets'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8'}
    id = Column("id", Integer, primary_key=True)
    text = Column(String(1024))
    photo_url = Column(String(1024))
    date = Column(DateTime, nullable=True)

    def __init__(self, text=None, photo_url=None, date=None):
        self.text = text
        self.photo_url = photo_url
        self.date = date
