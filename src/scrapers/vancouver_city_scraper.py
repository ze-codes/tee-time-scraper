from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .base_scraper import BaseScraper
from typing import List, Dict
from datetime import datetime, timedelta
import time
import pytz
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re

class VancouverCityScraper(BaseScraper):
    def __init__(self):
        self.base_url = "https://secure.west.prophetservices.com/CityofVancouver/Home/nIndex?CourseId=2,1,3&Date="
        super().__init__(self.base_url)
        self.timezone = pytz.timezone('America/Vancouver')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.page_load_delay = 3  # seconds
        print("VancouverCityScraper initialized")

    async def scrape(self) -> List[Dict]:
        print("Starting scrape for Vancouver City golf courses")
        all_tee_times = []

        current_date = datetime.now(self.timezone).date()
        for i in range(5):  # Scrape for 5 days
            date_to_scrape = current_date + timedelta(days=i)
            formatted_date = date_to_scrape.strftime("%Y-%-m-%-d")
            url = f"{self.base_url}{formatted_date}"
            
            print(f"Scraping for date: {formatted_date}")
            self.driver.get(url)
            time.sleep(self.page_load_delay)
            
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "teeSheet"))
                )
                
                # Click "Show More Times" button until all tee times are visible
                while True:
                    try:
                        show_more_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.ID, "btnShowMoreTimes"))
                        )
                        self.driver.execute_script("arguments[0].click();", show_more_button)
                        time.sleep(1)  # Wait for new tee times to load
                    except TimeoutException:
                        break  # No more "Show More Times" button, all tee times are visible

                # Get all tee times, including previously hidden ones
                tee_time_elements = self.driver.find_elements(By.CSS_SELECTOR, ".teeSheet .teetime")
                
                for element in tee_time_elements:
                    try:
                        raw_data = self.extract_raw_data(element, date_to_scrape)
                        parsed_data = await self.parse_tee_time(raw_data)
                        if parsed_data:
                            all_tee_times.append(parsed_data)
                    except ValueError as e:
                        print(f"Skipping tee time due to error: {str(e)}")
                    except Exception as e:
                        print(f"Unexpected error processing tee time: {str(e)}")
                
            except Exception as e:
                print(f"Error scraping date {formatted_date}: {str(e)}")

        self.driver.quit()
        print(f"Scraping completed. Total tee times found: {len(all_tee_times)}")
        return all_tee_times

    def extract_raw_data(self, element, date) -> Dict:
        try:
            time_text = element.get_attribute("teetime")
            if not time_text:
                time_element = element.find_element(By.CSS_SELECTOR, ".timeDiv span")
                time_text = time_element.text.strip()
            if not time_text:
                raise ValueError("Time not found")
            print(f"Raw time text: '{time_text}'")
            # Remove all whitespace and newline characters
            time_text = ''.join(time_text.split())
            time_match = re.search(r'(\d{2}:\d{2})', time_text)
            if time_match:
                time = time_match.group(1)
                print(f"Extracted time: {time}")
            else:
                raise ValueError("Time not found in: " + time_text)
        except NoSuchElementException:
            raise ValueError("Time element not found")

        try:
            price_element = element.find_element(By.CSS_SELECTOR, ".priceDiv h3")
            price_text = price_element.text.strip()
            if not price_text:
                price_text = element.get_attribute("data-price")
            price_match = re.search(r'\$?(\d+(\.\d{2})?)', price_text)
            if price_match:
                price = price_match.group(1)
            else:
                raise ValueError("No valid price found in: " + price_text)
        except NoSuchElementException:
            raise ValueError("Price element not found")

        try:
            course_name = element.find_element(By.CSS_SELECTOR, ".p-nopadding p").text.strip()
            if not course_name:
                course_div = element.find_element(By.CSS_SELECTOR, "div[name^='course-']")
                course_name = course_div.get_attribute("name").replace("course-", "")
            if not course_name:
                raise ValueError("Course name not found")
        except NoSuchElementException:
            raise ValueError("Course name element not found")

        try:
            players = element.find_element(By.CSS_SELECTOR, ".player p").text.strip()
            if not players:
                players = element.get_attribute("data-player")
            if not players:
                raise ValueError("Players information not found")
        except NoSuchElementException:
            raise ValueError("Players element not found")

        print(f"Raw data: Date: {date}, Time: {time}, Price: {price}, Course: {course_name}, Players: {players}")
        return {
            'date': date,
            'time': time,
            'price': price,
            'course_name': course_name,
            'players': players
        }

    async def parse_tee_time(self, raw_data: Dict) -> Dict:
        date = raw_data['date']
        time = raw_data['time']
        if not time:
            print(f"Error: Time is None for date {date}")
            return None
        datetime_str = f"{date} {time}"
        try:
            naive_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Error parsing datetime: {datetime_str}")
            return None
        
        localized_datetime = self.timezone.localize(naive_datetime)
        utc_datetime = localized_datetime.astimezone(pytz.UTC)
        print(f"Localized datetime: {localized_datetime}, UTC datetime: {utc_datetime}")
        
        try:
            price = float(raw_data['price'])
        except ValueError:
            price = 0.0
        
        players_str = raw_data['players'].lower().replace('players', '').strip()
        if 'to' in players_str:
            min_players, max_players = map(int, players_str.split('to'))
            min_players = max(2, min_players)  # Ensure minimum of 2 players
            available_booking_sizes = list(range(min_players, max_players + 1))
        else:
            try:
                available_booking_sizes = [max(2, int(players_str))]
            except ValueError:
                available_booking_sizes = [2]  # Default to 2 players if parsing fails
        
        parsed_data = {
            'datetime': utc_datetime.isoformat(),
            'price': price,
            'currency': 'CAD',
            'available_booking_sizes': available_booking_sizes,
            'course_name': raw_data['course_name'],
            'starting_hole': 1,  # Assuming all start from hole 1, adjust if needed
        }
        print(f"Parsed data: {parsed_data}")
        return parsed_data

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
        print("VancouverCityScraper instance destroyed")