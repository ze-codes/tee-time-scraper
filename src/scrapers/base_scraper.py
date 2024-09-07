import abc
from typing import List, Dict

class BaseScraper(abc.ABC):
    def __init__(self, url: str):
        self.url = url

    @abc.abstractmethod
    async def scrape(self) -> List[Dict]:
        """
        Scrape tee times from the website.
        Returns a list of dictionaries containing tee time data.
        """
        pass

    @abc.abstractmethod
    async def parse_tee_time(self, raw_data: Dict) -> Dict:
        """
        Parse raw tee time data into a standardized format.
        """
        pass
