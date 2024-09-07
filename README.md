# Tee Time Scraper

This project is a web scraper designed to collect tee time data from various golf course websites and store it in a PostgreSQL database. It's built to work alongside a separate user-facing tee-time booking web app.

## Features

- Scrapes tee time data from Mayfair Lakes golf course website
- Stores collected data in a PostgreSQL database
- Modular design for easy addition of new website scrapers
- Asynchronous scraping for improved efficiency
- Timezone-aware datetime handling for Vancouver (PST/PDT)

## Prerequisites

- Python 3.7+
- PostgreSQL database
- Chrome browser (for Selenium WebDriver)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/tee-time-scraper.git
   cd tee-time-scraper
   ```

2. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your PostgreSQL database and update the `.env` file with your database credentials.

5. Copy `.env.example` to `.env` and fill in your configuration details.

## Usage

Run the main script to start scraping:

```
python src/main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.