from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, query, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    stage = Column(Integer, default=0)

    def __init__(self, name, stage):
        self.name = name
        self.stage = stage

class Cars(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    three_days = Column(Integer)
    weeks = Column(Integer)
    two_weeks = Column(Integer)
    three_weeks = Column(Integer)
    month = Column(Integer)
    long_per_day = Column(Integer)
    long = Column(Integer)
    text = Column(String)

    def __init__(self, name, three_days, weeks, two_weeks, three_weeks, month, long_per_day, long, text):
        self.name = name
        self.three_days = three_days
        self.weeks = weeks
        self.two_weeks = two_weeks
        self.three_weeks = three_weeks
        self.month = month
        self.long_per_day = long_per_day
        self.long = long
        self.text = text

class Info(Base):
    __tablename__ = "info"
    id = Column(Integer, primary_key=True)
    text = Column(String)
    message_id = Column(Integer)

    def __init__(self, text, message_id):
        self.text = text
        self.message_id = message_id

engine = create_engine("postgresql://postgres:123@db:5432/bot")
Session = sessionmaker(bind=engine)
session = Session()


def create_db():
    Base.metadata.create_all(engine)

create_db()