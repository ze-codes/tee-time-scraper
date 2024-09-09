from sqlalchemy.orm import Session
from ..models.tee_time import Course, TeeTime, Player
from datetime import datetime
from typing import Dict

class TeeTimeRepository:
    def __init__(self, db: Session):
        self.db = db

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

    def get_tee_times(self, filters: Dict, page: int, limit: int, sort: str, order: str) -> Dict:
        query = self.db.query(TeeTime).join(Course).outerjoin(Player)

        # Apply filters
        if 'starttime' in filters and 'endtime' in filters:
            query = query.filter(TeeTime.datetime.between(filters['starttime'], filters['endtime']))
        if 'course' in filters:
            query = query.filter(Course.name.in_(filters['course']))
        if 'distance' in filters:
            # Implement distance filtering (requires geospatial calculations)
            pass
        if 'availability' in filters:
            query = query.filter(TeeTime.available_spots >= filters['availability'])
        if 'startage' in filters and 'endage' in filters:
            query = query.filter(Player.age.between(filters['startage'], filters['endage']))
        if 'gender' in filters:
            query = query.filter(Player.gender == filters['gender'])
        if 'race' in filters:
            query = query.filter(Player.race == filters['race'])
        if 'socialLevel' in filters:
            query = query.filter(Player.social_level == filters['socialLevel'])
        if 'handicap' in filters:
            query = query.filter(Player.handicap == filters['handicap'])

        # Apply sorting
        if sort == 'time':
            query = query.order_by(TeeTime.datetime.asc() if order == 'asc' else TeeTime.datetime.desc())
        elif sort == 'price':
            query = query.order_by(TeeTime.price.asc() if order == 'asc' else TeeTime.price.desc())
        # Add more sorting options as needed

        # Get total count for pagination
        total_items = query.count()

        # Apply pagination
        query = query.offset((page - 1) * limit).limit(limit)

        tee_times = query.all()

        return {
            "teeTimes": [self.format_tee_time(tee_time) for tee_time in tee_times],
            "pagination": {
                "currentPage": page,
                "totalPages": (total_items + limit - 1) // limit,
                "totalItems": total_items,
                "itemsPerPage": limit
            }
        }

    def format_tee_time(self, tee_time: TeeTime) -> Dict:
        return {
            "id": tee_time.id,
            "course": tee_time.course.name,
            "time": tee_time.datetime.strftime("%H:%M"),
            "availability": tee_time.available_spots,
            "price": tee_time.price,
            "distance": 0,  # Implement distance calculation
            "players": [
                {
                    "gender": player.gender,
                    "age": player.age,
                    "race": player.race,
                    "socialLevel": player.social_level.value,
                    "handicap": player.handicap.value
                } for player in tee_time.players
            ]
        }