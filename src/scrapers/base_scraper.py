import logging
import time
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class BaseScraper:
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        proxy_list: Optional[list] = None,
        timeout: int = 10,
        verify_ssl: bool = True
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.proxy_list = proxy_list
        self.current_proxy_index = 0

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        # Create session with retry logic
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Rotate through proxy list in round-robin fashion"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return {"http": proxy, "https": proxy}

    def make_request(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        data: Any = None,
        json_data: Any = None
    ) -> requests.Response:
        """Make HTTP request with retry logic and proxy support"""
        try:
            proxies = self._get_next_proxy()
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json_data,
                timeout=self.timeout,
                verify=self.verify_ssl,
                proxies=proxies
            )
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise

    def scrape(self, url: str) -> Dict[str, Any]:
        """Template method to be implemented by concrete scrapers"""
        raise NotImplementedError("Concrete scrapers must implement scrape method")

    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Template method for cleaning scraped data"""
        return data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()