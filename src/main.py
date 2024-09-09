from dotenv import load_dotenv
load_dotenv()  # Add this at the beginning of your main.py

from database.db_config import Base, engine

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
