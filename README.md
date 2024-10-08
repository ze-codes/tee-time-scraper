# Tee Time Scraper and API

This project is a comprehensive solution for scraping, storing, and serving tee time data from various golf courses. It combines web scraping capabilities with a robust API to provide up-to-date tee time information.

## Features

- Web scraping of tee time data from multiple golf course websites
- Storage of tee time information in a PostgreSQL database
- RESTful API for querying and filtering tee time data
- Asynchronous scraping for improved efficiency
- Timezone-aware datetime handling (Vancouver PST/PDT)
- Modular design for easy addition of new golf course scrapers
- Integration with Firebase/Firestore for additional data storage options
- Automatic expiration of past tee times

## Tech Stack

- Python 3.7+
- FastAPI for API development
- SQLAlchemy for ORM and database operations
- Selenium WebDriver for web scraping
- PostgreSQL for primary data storage
- Firebase/Firestore for additional data storage
- Pydantic for data validation

## Prerequisites

- Python 3.7+
- PostgreSQL database
- Chrome browser (for Selenium WebDriver)
- Firebase project (optional, for Firestore integration)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/your-username/tee-time-scraper.git
   cd tee-time-scraper
   ```

2. Create and activate a virtual environment:

   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up your environment:

   - Copy `.env.example` to `.env`
   - Fill in your PostgreSQL and Firebase credentials in the `.env` file

5. Database Setup:

   - Ensure PostgreSQL is installed and running
   - Create a new database named `golf_tee_times`:
     ```
     psql -U your_username
     CREATE DATABASE golf_tee_times;
     \q
     ```
   - Update the `DB_NAME` in your `.env` file:
     ```
     DB_NAME=golf_tee_times
     ```

6. Initialize the database:
   ```
   python src/scripts/init_db.py
   ```
   This will create the necessary tables in your database.

## Running the Application

1. Start the FastAPI server:

   ```
   uvicorn src.api.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

2. Access the interactive API documentation at `http://localhost:8000/docs`.

3. (Optional) Add or update course information:
   ```
   python src/scripts/manage_courses.py
   ```

## Usage

### API Endpoints

- `GET /api/tee-times/all`: Retrieve all tee times (paginated)
- `GET /api/tee-times/available`: Retrieve all available tee times (paginated)
- `POST /scrape`: Manually trigger the scraping process for a specific course
- `GET /available-courses`: Get a list of available courses for scraping

### Scraping a Specific Course

To scrape a specific course, send a POST request to `/scrape` with the `course` query parameter:

```
curl -X POST "http://localhost:8000/scrape?course=mayfair_lakes"
```

### Getting Available Courses

To get a list of available courses for scraping, send a GET request to `/available-courses`:

```
curl http://localhost:8000/available-courses
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Data Model

### TeeTime

- `id`: Unique identifier for the tee time
- `course_id`: Foreign key to the associated course
- `datetime`: Date and time of the tee time
- `price`: Price of the tee time
- `currency`: Currency of the price
- `available_booking_sizes`: Array of available booking sizes. An empty array indicates the tee time is unavailable.
- `starting_hole`: The starting hole for the tee time

Note: A tee time is considered unavailable if its `available_booking_sizes` array is empty.

## Internal Workflows

### Tee Time Expiration

The system automatically checks for expired tee times every 2 minutes. Any tee time that has passed its scheduled datetime will be marked as unavailable by setting its `available_booking_sizes` to an empty array.
