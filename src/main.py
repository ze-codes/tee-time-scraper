from dotenv import load_dotenv
load_dotenv()  # Add this at the beginning of your main.py

import asyncio
from scrapers.site1_scraper import MayfairLakesScraper
from database.repositories.tee_time_repository import TeeTimeRepository
from database.db_config import Base, engine

async def main():
    # Create tables
    Base.metadata.create_all(bind=engine)

    scrapers = [MayfairLakesScraper()]
    tee_time_repository = TeeTimeRepository()
    
    for scraper in scrapers:
        tee_times = await scraper.scrape()
        
        # Save tee times to PostgreSQL
        tee_time_repository.save_tee_times(scraper.course_name, tee_times)
        
        for tee_time in tee_times:
            print(f"Course: {tee_time['course_name']}, Tee Time: {tee_time['datetime']}, "
                  f"Price: ${tee_time['price']:.2f} {tee_time['currency']}, "
                  f"Available Spots: {tee_time['available_spots']}, "
                  f"Starting Hole: {tee_time['starting_hole']}")

if __name__ == "__main__":
    asyncio.run(main())
