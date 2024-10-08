from sqlalchemy.orm import Session
from ..models.tee_time import Course, TeeTime, Player
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy import and_, desc
import pytz

class TeeTimeRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_tee_times(self, tee_times: List[Dict]):
        try:
            # Create a dictionary to store courses
            courses = {}
            
            # Get all course names from the tee times
            course_names = set(tt['course_name'] for tt in tee_times)
            
            # Fetch or create courses
            for course_name in course_names:
                course = self.db.query(Course).filter(Course.name == course_name).first()
                if not course:
                    course = Course(name=course_name)
                    self.db.add(course)
                    self.db.flush()
                courses[course_name] = course
            
            current_time = datetime.now(timezone.utc)
            
            for course_name, course in courses.items():
                # Get all existing tee times for this course
                existing_tee_times = self.db.query(TeeTime).filter(TeeTime.course_id == course.id).all()
                
                # Create a set of datetime objects from the scraped tee times for easy comparison
                scraped_datetimes = {datetime.fromisoformat(tt['datetime']) for tt in tee_times if tt['course_name'] == course_name}
                
                for existing_tee_time in existing_tee_times:
                    # Ensure existing_tee_time.datetime is timezone-aware
                    if existing_tee_time.datetime.tzinfo is None:
                        existing_tee_time.datetime = existing_tee_time.datetime.replace(tzinfo=timezone.utc)
                    
                    # Case 1: Mark past tee times as unavailable
                    if existing_tee_time.datetime < current_time:
                        existing_tee_time.available_booking_sizes = []
                    # Case 2: Mark tee times not in the latest scrape as unavailable (only for the courses being scraped)
                    elif existing_tee_time.datetime.date() in [datetime.fromisoformat(tt['datetime']).date() for tt in tee_times if tt['course_name'] == course_name]:
                        if existing_tee_time.datetime not in scraped_datetimes:
                            existing_tee_time.available_booking_sizes = []
                
                # Update or create tee times
                for tee_time in tee_times:
                    if tee_time['course_name'] == course_name:
                        tee_time_datetime = datetime.fromisoformat(tee_time['datetime'])
                        existing_tee_time = next((tt for tt in existing_tee_times if tt.datetime == tee_time_datetime), None)

                        if existing_tee_time:
                            # Update existing tee time
                            existing_tee_time.price = tee_time['price']
                            existing_tee_time.available_booking_sizes = tee_time['available_booking_sizes']
                        else:
                            # Create new tee time
                            new_tee_time = TeeTime(
                                course_id=course.id,
                                datetime=tee_time_datetime,
                                price=tee_time['price'],
                                currency=tee_time['currency'],
                                available_booking_sizes=tee_time['available_booking_sizes'],
                                starting_hole=tee_time['starting_hole']
                            )
                            self.db.add(new_tee_time)

            self.db.commit()
            print(f"Successfully saved and updated tee times for {len(courses)} courses")
        except Exception as e:
            self.db.rollback()
            print(f"Error saving tee times: {str(e)}")
            raise

    def get_all_tee_times(self, page: int, limit: int, sort_by: Optional[str], sort_order: str) -> Dict:
        query = self.db.query(TeeTime).join(Course).outerjoin(Player)
        query = self._apply_sorting(query, sort_by, sort_order)
        return self._paginate_query(query, page, limit)

    def get_all_available_tee_times(self, page: int, limit: int, sort_by: Optional[str], sort_order: str) -> Dict:
        query = self.db.query(TeeTime).join(Course).outerjoin(Player).filter(TeeTime.available_booking_sizes != [])
        query = self._apply_sorting(query, sort_by, sort_order)
        return self._paginate_query(query, page, limit)

    def _paginate_query(self, query, page: int, limit: int) -> Dict:
        total_items = query.count()
        tee_times = query.offset((page - 1) * limit).limit(limit).all()

        return {
            "teeTimes": [self._format_tee_time(tee_time) for tee_time in tee_times],
            "pagination": {
                "currentPage": page,
                "totalPages": (total_items + limit - 1) // limit,
                "totalItems": total_items,
                "itemsPerPage": limit
            }
        }

    def _format_tee_time(self, tee_time: TeeTime) -> Dict:
        course_timezone = pytz.timezone(tee_time.course.timezone)
        localized_datetime = tee_time.datetime.astimezone(course_timezone)
        
        return {
            "id": tee_time.id,
            "course": tee_time.course.name,
            "datetime": localized_datetime.isoformat(),
            "timezone": tee_time.course.timezone,
            "available_booking_sizes": tee_time.available_booking_sizes,
            "price": tee_time.price,
            "currency": tee_time.currency,
            "starting_hole": tee_time.starting_hole
        }

    def update_expired_tee_times(self):
        current_time = datetime.now(timezone.utc)
        expired_tee_times = self.db.query(TeeTime).filter(
            TeeTime.datetime < current_time,
            TeeTime.available_booking_sizes != []
        ).all()

        for tee_time in expired_tee_times:
            tee_time.available_booking_sizes = []

        self.db.commit()
        print(f"Updated {len(expired_tee_times)} expired tee times")

    def get_filtered_tee_times(self, date: Optional[str], course: Optional[str], min_price: Optional[float], max_price: Optional[float], page: int, limit: int, sort_by: Optional[str], sort_order: str) -> Dict:
        query = self.db.query(TeeTime).join(Course)

        if date:
            query = query.filter(TeeTime.datetime.cast(Date) == date)
        if course:
            query = query.filter(Course.name == course)
        if min_price is not None:
            query = query.filter(TeeTime.price >= min_price)
        if max_price is not None:
            query = query.filter(TeeTime.price <= max_price)

        query = query.filter(TeeTime.available_booking_sizes != [])  # Only get available tee times
        query = self._apply_sorting(query, sort_by, sort_order)

        return self._paginate_query(query, page, limit)

    def get_all_course_names(self) -> List[str]:
        courses = self.db.query(Course.name).distinct().all()
        return [course[0] for course in courses]

    def _apply_sorting(self, query, sort_by: Optional[str], sort_order: str):
        if sort_by:
            if hasattr(TeeTime, sort_by):
                order_func = desc if sort_order == 'desc' else None
                query = query.order_by(order_func(getattr(TeeTime, sort_by)) if order_func else getattr(TeeTime, sort_by))
            else:
                print(f"Warning: Invalid sort_by field '{sort_by}'. Ignoring sorting.")
        return query