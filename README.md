# Tee Time Scraper and API

This project is a comprehensive solution for scraping, storing, and serving tee time data from various golf courses. It combines web scraping capabilities with a robust API to provide up-to-date tee time information.

## Features

- Web scraping of tee time data from multiple golf course websites
- Storage of tee time information in a PostgreSQL database
- RESTful API for querying and filtering tee time data
- Asynchronous scraping for improved efficiency
- Scheduled daily scraping to keep data current
- Timezone-aware datetime handling (Vancouver PST/PDT)
- Modular design for easy addition of new golf course scrapers
- Integration with Firebase/Firestore for additional data storage options

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

5. Initialize the database:
   ```
   python src/main.py
   ```

## Usage

### Running the Scraper

To manually trigger the scraping process:

```
python src/main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.