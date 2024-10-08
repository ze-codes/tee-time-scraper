from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, ARRAY
from sqlalchemy.orm import relationship
from ..db_config import Base
import enum
from sqlalchemy.types import TypeDecorator
from datetime import datetime, timezone

class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.replace(tzinfo=timezone.utc)
        return value

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
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String, nullable=False, server_default="America/Vancouver")

    tee_times = relationship("TeeTime", back_populates="course")

class TeeTime(Base):
    __tablename__ = "tee_times"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    datetime = Column(TZDateTime, index=True)
    price = Column(Float)
    currency = Column(String)
    available_booking_sizes = Column(ARRAY(Integer)) 
    starting_hole = Column(Integer)

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