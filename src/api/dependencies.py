from src.database.db_config import get_db

def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()