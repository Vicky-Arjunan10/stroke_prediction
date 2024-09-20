from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float, Time
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

url = "postgresql+psycopg2://postgres:root@localhost:5432/stroke_prediction"
engine = create_engine(url)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class StrokePrediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(Date, default=func.now())
    created_time = Column(Time, default=func.now())
    source = Column(String)
    gender = Column(String)
    age = Column(Integer)
    hypertension = Column(Integer)
    heart_diseases = Column(Integer)
    glucose = Column(Float)
    bmi = Column(Float)
    result = Column(String)

Base.metadata.create_all(engine)



