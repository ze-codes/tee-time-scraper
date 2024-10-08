from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .base_scraper import BaseScraper
from typing import List, Dict
from datetime import datetime
import time
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import pytz

class MayfairLakesScraper(BaseScraper):
    def __init__(self):
        url = "https://mayfairlakes.totaleintegrated.com/Book-a-Tee-Time"
        super().__init__(url)
        self.course_name = "Mayfair Lakes"
        self.timezone = pytz.timezone('America/Vancouver')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        print("MayfairLakesScraper initialized")

    async def scrape(self) -> List[Dict]:
        print(f"Starting scrape for {self.url}")
        self.driver.get(self.url)
        
        all_tee_times = []
        calendar_item_index = 0
        
        while True:
        # for calendar_item_index in range(2):
            calendar_item_id = f"customcaleder_{calendar_item_index}"
            print(f"Attempting to find tee times for calendar item: {calendar_item_id}")
            
            try:
                calendar_item = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, calendar_item_id))
                )
                
                self.driver.execute_script("arguments[0].click();", calendar_item)
                print(f"Clicked on calendar item: {calendar_item_id}")
                
                # Wait for the page to update after clicking
                time.sleep(3)  # Add a 3-second delay

                # Wait for either tee times to load or "No Tee Times Available" message
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "dnn_ctr1325_DefaultView_ctl01_dlTeeTimes"))
                    )
                    print(f"Tee times found for calendar item: {calendar_item_id}")
                    
                    tee_times_found = True
                except TimeoutException:
                    print(f"No tee times available for calendar item: {calendar_item_id}")
                    tee_times_found = False
                
                if tee_times_found:
                    # Process tee times without date verification
                    tee_time_elements = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#dnn_ctr1325_DefaultView_ctl01_dlTeeTimes > span"))
                    )
                    print(f"Found {len(tee_time_elements)} tee time elements")
                    
                    for i, element in enumerate(tee_time_elements):
                        try:
                            print(f"Processing tee time {i+1}")
                            raw_data = self.extract_raw_data(element)
                            parsed_data = await self.parse_tee_time(raw_data)
                            if parsed_data not in all_tee_times:
                                all_tee_times.append(parsed_data)
                        except StaleElementReferenceException:
                            print(f"Stale element encountered for tee time {i+1}. Retrying...")
                            # Refresh the list of elements and retry
                            tee_time_elements = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#dnn_ctr1325_DefaultView_ctl01_dlTeeTimes > span"))
                            )
                            if i < len(tee_time_elements):
                                element = tee_time_elements[i]
                                raw_data = self.extract_raw_data(element)
                                parsed_data = await self.parse_tee_time(raw_data)
                                if parsed_data not in all_tee_times:
                                    all_tee_times.append(parsed_data)
                            else:
                                print(f"Tee time {i+1} no longer available")
                        except Exception as e:
                            print(f"Error processing tee time {i+1}: {str(e)}")
                
                time.sleep(2)
                calendar_item_index += 1
                
            except TimeoutException:
                print(f"Calendar item {calendar_item_id} not found. Scraping complete.")
                break
            except Exception as e:
                print(f"An error occurred while processing {calendar_item_id}: {str(e)}")
                break
        
        self.driver.quit()
        print(f"Scraping completed. Total tee times found: {len(all_tee_times)}")
        return all_tee_times

    def extract_raw_data(self, element) -> Dict:
        date = element.find_element(By.CSS_SELECTOR, "span[id^='dnn_ctr1325_DefaultView_ctl01_dlTeeTimes_lblTeeDate_']").text
        time = element.find_element(By.CSS_SELECTOR, "span[id^='dnn_ctr1325_DefaultView_ctl01_dlTeeTimes_lblTeeTime_']").text
        price = element.find_element(By.CSS_SELECTOR, "span[id^='dnn_ctr1325_DefaultView_ctl01_dlTeeTimes_lblPlayers_']").text
        availability = element.find_element(By.CSS_SELECTOR, "select[id^='ddlNumPlayers']").get_attribute('textContent')
        course_name = element.find_element(By.CSS_SELECTOR, "span[id^='dnn_ctr1325_DefaultView_ctl01_dlTeeTimes_lblCourseName_']").text
        starting_hole = element.find_element(By.CSS_SELECTOR, "span[id^='dnn_ctr1325_DefaultView_ctl01_dlTeeTimes_lblStartTee_']").text
        
        print(f"Raw data: Date: {date}, Time: {time}, Price: {price}, Availability: {availability}, Course: {course_name}, Starting Hole: {starting_hole}")
        return {
            'date': date,
            'time': time,
            'price': price,
            'availability': availability,
            'course_name': course_name,
            'starting_hole': starting_hole
        }

    async def parse_tee_time(self, raw_data: Dict) -> Dict:
        date = raw_data['date']
        time = raw_data['time'].split()[0] + ' ' + raw_data['time'].split()[1]  # Extract only the time part
        datetime_str = f"{date} {time}"
        naive_datetime = datetime.strptime(datetime_str, "%m/%d/%Y %I:%M %p")
        
        # Localize the naive datetime to Vancouver time
        localized_datetime = self.timezone.localize(naive_datetime)
        
        # Convert to UTC before returning
        utc_datetime = localized_datetime.astimezone(pytz.UTC)
        print(
            f"Localized datetime: {localized_datetime}, UTC datetime: {utc_datetime}"
        )
        
        price = float(raw_data['price'].split('$')[1].split('/')[0])
        
        availability_str = raw_data['availability'].strip()
        availability = []
        for option in availability_str.split('\n'):
            option = option.strip()
            if '-' in option:
                start, end = map(int, option.split('-'))
                availability.extend(range(start, end + 1))
            elif option.isdigit():
                availability.append(int(option))
        availability = sorted(set(availability))  # Remove duplicates and sort
        
        starting_hole = ''.join(filter(str.isdigit, raw_data['starting_hole']))
        starting_hole = int(starting_hole) if starting_hole else 1  # Default to 1 if no digits found
        
        parsed_data = {
            'datetime': utc_datetime.isoformat(),
            'price': price,
            'currency': 'CAD',
            'available_booking_sizes': availability,
            'course_name': raw_data['course_name'],
            'starting_hole': starting_hole
        }
        print(f"Parsed data: {parsed_data}")
        return parsed_data

    def get_expected_date(self, calendar_index):
        # Implement logic to calculate the expected date based on the calendar index
        # This will depend on how the website structures its dates
        # For example:
        from datetime import datetime, timedelta
        base_date = datetime.now().date()
        expected_date = base_date + timedelta(days=calendar_index)
        return expected_date.strftime("%m/%d/%Y")

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
        print("MayfairLakesScraper instance destroyed")
