from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..db_config import Base
import enum

class SocialLevel(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Handicap(enum.Enum):
    under_10 = "<10"
    ten_to_twenty = "10-20"
    twenty_to_thirty = "20-30"
    over_thirty = "30+"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

class TeeTime(Base):
    __tablename__ = "tee_times"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    datetime = Column(DateTime, index=True)
    price = Column(Float)
    currency = Column(String)
    available_spots = Column(Integer)
    starting_hole = Column(Integer)
    status = Column(String, default="available")

    course = relationship("Course", back_populates="tee_times")
    players = relationship("Player", back_populates="tee_time")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    tee_time_id = Column(Integer, ForeignKey("tee_times.id"))
    gender = Column(String)
    age = Column(Integer)
    race = Column(String)
    social_level = Column(Enum(SocialLevel))
    handicap = Column(Enum(Handicap))

    tee_time = relationship("TeeTime", back_populates="players")

Course.tee_times = relationship("TeeTime", order_by=TeeTime.datetime, back_populates="course")