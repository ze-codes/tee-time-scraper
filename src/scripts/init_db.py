from dotenv import load_dotenv
load_dotenv()

from src.database.db_config import Base, engine
import src.database.models  # This will import all models

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")