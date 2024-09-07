from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from ..db_config import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class TeeTime(Base):
    __tablename__ = "tee_times"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    datetime = Column(DateTime, index=True)
    price = Column(Float)
    currency = Column(String)
    available_spots = Column(ARRAY(Integer))
    starting_hole = Column(Integer)
    status = Column(String, default="available")

    course = relationship("Course", back_populates="tee_times")

Course.tee_times = relationship("TeeTime", order_by=TeeTime.datetime, back_populates="course")