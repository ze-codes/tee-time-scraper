# Tee Time Scraper

This project is a web scraper designed to collect tee time data from various golf course websites and store it in a Firestore database. It's built to work alongside a separate user-facing tee-time booking web app.

## Features

- Scrapes tee time data from multiple golf course websites
- Stores collected data in Firestore
- Modular design for easy addition of new website scrapers
- Asynchronous scraping for improved efficiency

## Prerequisites

- Python 3.7+
- Firebase account and project set up

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

4. Set up your Firestore credentials:
   - Download your Firebase Admin SDK private key JSON file
   - Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of this file

5. Copy `config.yml.example` to `config.yml` and fill in your configuration details.

## Usage

Run the main script to start scraping:

```
python src/main.py
```

## Project Structure

```
tee-time-scraper/
├── src/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── site1_scraper.py
│   │   └── site2_scraper.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── firestore_handler.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── main.py
├── tests/
│   ├── test_scrapers.py
│   └── test_database.py
├── requirements.txt
├── .gitignore
├── README.md
└── config.yml
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.