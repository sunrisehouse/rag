from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from collections import deque
import re
from urllib.parse import urljoin, urlparse
import os
import platform

# Local imports
from . import config
from . import database
from .logger import log

class Crawler:
    """웹 페이지를 크롤링하는 범용 클래스."""

    def __init__(self, crawl_job_id):
        """크롤러를 초기화하고 설정에 맞는 웹 드라이버를 설정합니다."""
        if not crawl_job_id:
            raise ValueError("A valid crawl_job_id must be provided.")
        
        self.crawl_job_id = crawl_job_id
        self.driver = self._setup_driver()
        
        self.confluence_url = config.CONFLUENCE_URL
        self.start_url = config.START_URL
        self.confluence_netloc = urlparse(self.confluence_url).netloc
        self.start_netloc = urlparse(self.start_url).netloc
        
        self.queue = deque([(self.start_url, None)])
        self.visited_urls = database.get_crawled_urls(self.crawl_job_id)
        self.crawled_pages_count = 0

    def _setup_driver(self):
        """config.BROWSER 설정에 따라 적절한 WebDriver를 초기화합니다."""
        browser_type = config.BROWSER.lower()
        log.info(f"Setting up webdriver for: {browser_type}")

        options = None
        service = None
        driver_path = None

        if browser_type == "chrome":
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # Determine the correct chromedriver for the OS
            system = platform.system()
            if system == "Darwin":  # macOS
                driver_filename = "chromedriver_mac"
            elif system == "Windows":
                driver_filename = "chromedriver_win.exe"
            elif system == "Linux":
                driver_filename = "chromedriver_linux"
            else:
                raise OSError(f"Unsupported operating system: {system}")

            driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', driver_filename))
            if not os.path.exists(driver_path):
                raise FileNotFoundError(
                    f"Chrome WebDriver not found for {system} at '{driver_path}'. "
                    f"Please download the correct driver for your OS and Chrome version, "
                    f"and place it in the 'crawler/resources' directory with the name '{driver_filename}'."
                )

            service = Service(executable_path=driver_path)
            return webdriver.Chrome(service=service, options=options)
        
        elif browser_type == "edge":
            from selenium.webdriver.edge.service import Service
            from selenium.webdriver.edge.options import Options
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Adjust the path ../resources to your project structure
            driver_filename = "msedgedriver"
            if platform.system() == "Windows":
                driver_filename += ".exe"
            driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', driver_filename))
            service = Service(executable_path=driver_path)
            return webdriver.Edge(service=service, options=options)
        
        elif browser_type == "firefox":
            from selenium.webdriver.firefox.service import Service
            from selenium.webdriver.firefox.options import Options
            options = Options()
            options.add_argument("--headless")
            
            # Adjust the path ../resources to your project structure
            driver_filename = "geckodriver"
            if platform.system() == "Windows":
                driver_filename += ".exe"
            driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', driver_filename))
            service = Service(executable_path=driver_path)
            return webdriver.Firefox(service=service, options=options)

        else:
            raise ValueError(f"Unsupported browser: '{config.BROWSER}'. Please choose 'chrome', 'edge', or 'firefox'.")

    def _login(self):
        """설정된 사이트에 로그인합니다."""
        log.info("Attempting to log in...")
        self.driver.get(self.confluence_url)
        
        try:
            # Confluence 기준 로그인 (필요시 다른 사이트에 맞게 수정)
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "os_username"))
            )
            username_field.send_keys(config.USERNAME)
            
            password_field = self.driver.find_element(By.ID, "os_password")
            password_field.send_keys(config.PASSWORD)
            
            login_button = self.driver.find_element(By.ID, "loginButton")
            login_button.click()
            
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "com-atlassian-confluence"))
            )
            log.info("Login successful.")
        except Exception as e:
            log.critical(f"Login failed. Please check credentials, network, or element selectors. Error: {e}")
            self.close()
            exit()

    def _is_valid_url(self, url):
        """크롤링할 유효한 URL인지 확인합니다."""
        # Check if the URL matches the allowed regex and does not have a file extension
        is_allowed = re.search(config.ALLOWED_URL_REGEX, url)
        not_file_extension = not re.search(r'\\.(jpg|jpeg|png|gif|pdf|zip|css|js)$', url, re.IGNORECASE)
        
        return is_allowed and not_file_extension

    def _resolve_url(self, href, base_url):
        """상대 URL을 절대 URL로 변환합니다."""
        return urljoin(base_url, href)

    def crawl(self):
        """크롤링을 시작하고 페이지를 순회합니다."""
        if config.LOGIN_REQUIRED:
            self._login()
            
        log.info(f"Starting crawl from: {self.start_url}")
        
        while self.queue:
            current_url, parent_url = self.queue.popleft()
            
            if current_url in self.visited_urls:
                log.debug(f"Skipping already visited URL: {current_url}")
                continue
            
            log.info(f"Crawling: {current_url}")
            try:
                self.driver.get(current_url)
                time.sleep(3)  # JavaScript 렌더링 대기
                html_content = self.driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                
                database.save_crawled_page(self.crawl_job_id, current_url, html_content, parent_url)
                self.visited_urls.add(current_url)
                self.crawled_pages_count += 1
                
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    next_url = self._resolve_url(href, current_url)
                    is_valid = self._is_valid_url(next_url)
                    
                    if is_valid and next_url not in self.visited_urls:
                        self.queue.append((next_url, current_url))
                
                time.sleep(config.CRAWL_DELAY)

            except Exception as e:
                log.error(f"Error crawling {current_url}: {e}")
                
        log.info(f"Crawling finished. Total pages crawled: {self.crawled_pages_count}")

    def close(self):
        """WebDriver를 종료합니다."""
        if self.driver:
            self.driver.quit()
            log.info("Browser closed.")
