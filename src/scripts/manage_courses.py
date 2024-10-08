import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).resolve().parents[1]
sys.path.append(str(src_path))

from database.db_config import SessionLocal, engine
from database.models.tee_time import Course, Base
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_courses(db: Session):
    return db.query(Course).all()

def update_course_info(db: Session, course_id: int, latitude: float, longitude: float, timezone: str):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        course.latitude = latitude
        course.longitude = longitude
        course.timezone = timezone
        db.commit()
        print(f"Updated information for {course.name}")
    else:
        print(f"Course with ID {course_id} not found")

def main():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())

    while True:
        courses = get_all_courses(db)
        
        if not courses:
            print("No courses found in the database.")
            add_new = input("Would you like to add a new course? (y/n): ")
            if add_new.lower() != 'y':
                break
            
            name = input("Enter course name: ")
            latitude = float(input("Enter latitude: "))
            longitude = float(input("Enter longitude: "))
            timezone = input("Enter timezone (e.g., America/Vancouver): ")
            new_course = Course(name=name, latitude=latitude, longitude=longitude, timezone=timezone)
            db.add(new_course)
            db.commit()
            print(f"Added new course: {name}")
            continue

        print("\nAvailable courses:")
        for course in courses:
            print(f"{course.id}: {course.name} (Lat: {course.latitude}, Long: {course.longitude}, Timezone: {course.timezone})")
        
        choice = input("\nEnter the ID of the course to update (or 'q' to quit): ")
        if choice.lower() == 'q':
            break
        
        try:
            course_id = int(choice)
            latitude = float(input("Enter latitude: "))
            longitude = float(input("Enter longitude: "))
            timezone = input("Enter timezone (e.g., America/Vancouver): ")
            update_course_info(db, course_id, latitude, longitude, timezone)
        except ValueError:
            print("Invalid input. Please enter valid numeric values for course ID, latitude, and longitude.")

if __name__ == "__main__":
    main()