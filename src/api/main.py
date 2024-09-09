from fastapi import FastAPI, BackgroundTasks
from fastapi_utils.tasks import repeat_every
from contextlib import asynccontextmanager
import asyncio

from src.scrapers.site1_scraper import MayfairLakesScraper
from src.database.repositories.tee_time_repository import TeeTimeRepository
from src.database.db_config import get_db
from src.api.routers import tee_times

app = FastAPI()

app.include_router(tee_times.router, prefix="/api/tee-times", tags=["tee_times"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(scheduled_scrape())
    yield

@repeat_every(seconds=60 * 60 * 24)  # Run once a day
async def scheduled_scrape() -> None:
    await trigger_scrape()

@app.post("/scrape")
async def scrape_endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(trigger_scrape)
    return {"message": "Scraping task has been scheduled"}

async def trigger_scrape():
    scrapers = [MayfairLakesScraper()]
    db = next(get_db())
    tee_time_repository = TeeTimeRepository(db)
    
    for scraper in scrapers:
        tee_times = await scraper.scrape()
        tee_time_repository.save_tee_times(scraper.course_name, tee_times)
    
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)