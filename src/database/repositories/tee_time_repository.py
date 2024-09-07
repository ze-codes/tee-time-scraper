from sqlalchemy.orm import Session
from ..models.tee_time import Course, TeeTime
from ..db_config import get_db
from datetime import datetime

class TeeTimeRepository:
    def __init__(self):
        self.db = next(get_db())

    def save_tee_times(self, course_name: str, tee_times: list):
        course = self.db.query(Course).filter(Course.name == course_name).first()
        if not course:
            course = Course(name=course_name)
            self.db.add(course)
            self.db.commit()
            self.db.refresh(course)

        for tee_time in tee_times:
            existing_tee_time = self.db.query(TeeTime).filter(
                TeeTime.course_id == course.id,
                TeeTime.datetime == datetime.fromisoformat(tee_time['datetime'])
            ).first()

            if existing_tee_time:
                existing_tee_time.price = tee_time['price']
                existing_tee_time.available_spots = tee_time['available_spots']
            else:
                new_tee_time = TeeTime(
                    course_id=course.id,
                    datetime=datetime.fromisoformat(tee_time['datetime']),
                    price=tee_time['price'],
                    currency=tee_time['currency'],
                    available_spots=tee_time['available_spots'],
                    starting_hole=tee_time['starting_hole']
                )
                self.db.add(new_tee_time)

        self.db.commit()
        print(f"Updated tee times for {course_name}")

    def get_tee_times(self, course_name: str, date: datetime.date):
        course = self.db.query(Course).filter(Course.name == course_name).first()
        if not course:
            return []

        tee_times = self.db.query(TeeTime).filter(
            TeeTime.course_id == course.id,
            TeeTime.datetime >= date,
            TeeTime.datetime < date + timedelta(days=1)
        ).all()

        return tee_times