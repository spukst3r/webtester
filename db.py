from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine('sqlite:///db.sqlite3')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def get_session():
    return Session()


def query(column):
    return get_session().query(column)
