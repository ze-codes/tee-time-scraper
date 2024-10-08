from fastapi import FastAPI, BackgroundTasks, Query, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List, Optional
from sqlalchemy.orm import Session

from src.scrapers.mayfair_lakes_scraper import MayfairLakesScraper
from src.scrapers.vancouver_city_scraper import VancouverCityScraper
from src.database.repositories.tee_time_repository import TeeTimeRepository
from src.database.db_config import get_db
from src.api.routers import tee_times
from src.api.dependencies import get_db_session

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tee_times.router, prefix="/api/tee-times", tags=["tee_times"])

SCRAPERS = {
    "mayfair_lakes": MayfairLakesScraper,
    "vancouver_city": VancouverCityScraper
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.post("/scrape")
async def scrape_endpoint(background_tasks: BackgroundTasks, course: Optional[str] = Query(None, description="Course to scrape (optional)")):
    if course is not None and course not in SCRAPERS:
        return {"error": f"Invalid course. Available courses are: {', '.join(SCRAPERS.keys())}"}
    background_tasks.add_task(trigger_scrape, course)
    message = f"Scraping task for {course} has been scheduled" if course else "Scraping task for all courses has been scheduled"
    return {"message": message}

@app.get("/available-courses", response_model=List[str])
async def get_available_courses(db: Session = Depends(get_db_session)):
    tee_time_repository = TeeTimeRepository(db)
    return tee_time_repository.get_all_course_names()

@app.post("/update-expired-tee-times")
async def update_expired_tee_times_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_expired_tee_times)
    return {"message": "Task to update expired tee times has been scheduled"}

async def trigger_scrape(course: Optional[str] = None):
    db = next(get_db())
    tee_time_repository = TeeTimeRepository(db)
    
    try:
        if course:
            scrapers = [SCRAPERS[course]()]
        else:
            scrapers = [scraper() for scraper in SCRAPERS.values()]

        for scraper in scrapers:
            tee_times = await scraper.scrape()
            print(f"Scraped tee times: {tee_times}")
            tee_time_repository.save_tee_times(tee_times)
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
    finally:
        db.close()

async def update_expired_tee_times():
    db = next(get_db())
    tee_time_repository = TeeTimeRepository(db)
    try:
        tee_time_repository.update_expired_tee_times()
        print("Successfully updated expired tee times")
    except Exception as e:
        print(f"Error updating expired tee times: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)