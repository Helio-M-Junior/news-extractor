import re
import logging
import configparser
import requests as rq
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC


class NewsExtractor:
    """
    NewsExtractor class for extracting news data from a website using Selenium and performing various operations.

    Attributes:
        url (str): The URL of the website.
        search_phrase (str): The search phrase to be used for news extraction.
        section (str): The section of the news to filter.
        date_type (str): Type of date range to consider.
        months (int): The number of months to consider in the search.
        show_more (int): Number of additional pages to load.
        log_file (str): Path to the log file.
        output_excel (str): Path to the output Excel file.
        picture_output (str): Path to the directory where pictures will be saved.

    Methods:
        setup_driver(): Set up the Selenium webdriver.
        close_driver(): Close the Selenium webdriver.
        accept_cookies(): Accept cookies if a prompt is present.
        navigate_to_url(): Navigate to the specified URL.
        search_news(): Perform a search for news using the provided search phrase.
        sort_news(): Sort the search results based on specified criteria.
        extract_data(): Extract news data from the search results.
        download_picture(): Download pictures associated with the news.
        check_contains_money(): Check if news titles or descriptions contain money-related information.
        count_search_phrase(): Count the occurrences of the search phrase in news titles and descriptions.
        export_excel(): Export the extracted news data to an Excel file.
        run(): Execute the entire news extraction and processing workflow.
    """

    def __init__(self):
        """
        Initialize the NewsExtractor instance.
        """
        try:
            # Create a configparser object and read the settings from the config file
            config = configparser.ConfigParser()
            config.read('config.ini')

            # Initialize variables with values from the config file under the 'Variables' section
            self.url = config.get('Variables', 'url')
            self.search_phrase = config.get('Variables', 'search_phrase')
            self.section = config.get('Variables', 'section')
            self.date_type = config.get('Variables', 'date_type')
            self.months = int(config.get('Variables', 'months'))
            self.show_more = int(config.get('Variables', 'show_more'))

            # Initialize paths with values from the config file under the 'Paths' section
            self.output_excel = config.get('Paths', 'output_excel')
            self.picture_output = config.get('Paths', 'picture_output')
            
            
        except (configparser.Error, ValueError) as e:
            # Handle configuration file parsing errors
            logging.error(f"Error in configuration file: {e}")
            exit()
            
        # Initialize other variables
        self.driver = None
        self.wait = None
        self.data = []
        self.picture_path = []
        self.contains_money = []
        self.counter_title = []
        self.counter_description = []

    def setup_driver(self):
        """Set up the Selenium webdriver."""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("-headless=new")
        chrome_options.add_argument("--window-size=1280,700")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def close_driver(self):
        """Close the Selenium webdriver."""
        if self.driver:
            self.driver.quit()

    def accept_cookies(self):
        """Accept cookies if a prompt is present."""
        try:
            cookies = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div[3]/div[2]/button[2]')))
            sleep(1)
            cookies.click()
        except Exception as e:
            logging.error(f"Error accepting cookies: {e}")

    def navigate_to_url(self):
        """Navigate to the specified URL."""
        try:
            self.driver.get(self.url)
            self.accept_cookies()
        except Exception as e:
            logging.error(f"Error navigating to URL: {e}")

    def search_news(self):
        """Perform a search for news using the provided search phrase."""
        try:
            search_icon = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[2]/header/section[1]/div[1]/div[2]/button')))
            search_icon.click()
            search_field = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[2]/header/section[1]/div[1]/div[2]/div/form/div/input')))
            search_field.send_keys(self.search_phrase)
            search_field.submit()
            self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, '/html/body/div[2]/div[2]/main/div')))
        except Exception as e:
            logging.error(f"Error searching for news: {e}")

    def set_date_range(self):
        """
        Set the date range based on the specified number of months.
        If months is 0 or 1, consider the current month. Otherwise, calculate the start date based on the number of months.
        """
        if self.months == 0 or self.months == 1:
            self.start_date = datetime.now().replace(day=1)
            self.end_date = datetime.now()
        else:
            # Calculate start date based on the number of months
            self.end_date = datetime.now()
            self.start_date = self.end_date - timedelta(days=30 * (self.months - 1))

        self.start_date = self.start_date.strftime("%m/%d/%Y")
        self.end_date = self.end_date.strftime("%m/%d/%Y")

        return self.start_date, self.end_date

    def load_pages(self):
        """Load additional pages of news by clicking the 'Show More' button."""
        for _ in range(self.show_more):
            show_more_div = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'css-1t62hi8')))
            show_more_button = show_more_div.find_element(By.TAG_NAME, 'button')
            show_more_button.click()
            sleep(2)

    def sort_news(self):
        """Sort the search results based on specified criteria."""
        try:
            self.set_date_range()
            date_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/button')))
            date_button.click()
            opened_date = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/div/ul')))
            date_options = opened_date.find_elements(By.TAG_NAME,'li')

            for option in date_options:
                if self.date_type in option.text:
                    option.click()

            start_date_range = self.wait.until(EC.visibility_of_element_located((By.ID, 'startDate')))
            start_date_range.send_keys(self.start_date)
            end_date_range = self.wait.until(EC.visibility_of_element_located((By.ID, 'endDate')))
            end_date_range.send_keys(self.end_date)
            search_sortby = Select(self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/div/div[1]/div[1]/form/div[2]/div/select'))
            search_sortby.select_by_value('newest')
            section_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/main/div/div[1]/div[2]/div/div/div[2]/div/div/button')))
            section_button.click()
            opened_section = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'css-64f9ga')))
            section_options = opened_section.find_elements(By.TAG_NAME,'li')

            for option in section_options:
                if self.section in option.text:
                    option.click()

            section_button.click()
            self.load_pages()
        except Exception as e:
            logging.error(f"Error sorting news: {e}")

    def extract_data(self):
        """Extract news data from the search results."""
        try:
            search_results = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-testid="search-results"')))
            sleep(2)
            news_results = search_results.find_elements(By.TAG_NAME, 'li')
            for result in news_results:
                try:
                    date = result.find_element(By.CSS_SELECTOR, '[data-testid="todays-date"').text
                    title = result.find_element(By.TAG_NAME, 'h4').text
                    description = result.find_element(By.CLASS_NAME, 'css-16nhkrn').text
                    img = result.find_element(By.TAG_NAME, 'img')
                    picture_source = img.get_attribute('src')
                    news_info = {'Title': title, 'Date': date, 'Description': description, 'Picture Source': picture_source}
                    self.data.append(news_info)
                except Exception as e:
                    logging.error(f"Error extracting news data: {e}")
                    continue  # Continue to the next iteration if an error occurs
        except Exception as e:
            logging.error(f"Error extracting news data: {e}")

    def download_picture(self):
        """Download pictures associated with the news."""
        try:
            for news in self.data:
                picture_filename = ''.join(news['Title'].split()[:3])
                response = rq.get(news['Picture Source'])
                if response.status_code == 200:
                    with open(f"{self.picture_output}{picture_filename}.jpg", "wb") as file:
                        file.write(response.content)
                    self.picture_path.append({'Picture Filename': f'{self.picture_output}{picture_filename}.jpg'})
        except Exception as e:
            logging.error(f"Error downloading pictures: {e}")

    def check_contains_money(self):
        """Check if news titles or descriptions contain money-related information."""
        money_patterns = ['\$+\d+\.?\d+', '\$+\d+\,\d+\.?\d+', '\d+ dollars|\d+ USD']
        for news in self.data:
            news_contains_money = []
            for pattern in money_patterns:
                news_contains_money.append(re.search(pattern, news['Title']))
                news_contains_money.append(re.search(pattern, news['Description']))
            if not any(news_contains_money):
                self.contains_money.append(False)
            else:
                self.contains_money.append(True)

    def count_search_phrase(self):
        """Count the occurrences of the search phrase in news titles and descriptions."""
        for news in self.data:
            count_title = news['Title'].count(self.search_phrase)
            count_description = news['Description'].count(self.search_phrase)
            self.counter_title.append(count_title)
            self.counter_description.append(count_description)

    def export_excel(self):
        """Export the extracted news data to an Excel file."""
        try:
            table = pd.DataFrame(data=self.data)
            table.drop(columns=['Picture Source'], axis=1, inplace=True)
            table['Picture Filename'] = pd.Series(self.picture_path).apply(lambda x: x['Picture Filename'])
            table['Counter Title'] = self.counter_title
            table['Counter Description'] = self.counter_description
            table['Contains Money'] = self.contains_money

            table.to_excel(self.output_excel, index=False)
        except Exception as e:
            logging.error(f"Error exporting data to Excel: {e}")

    def run(self):
        """Execute the entire news extraction and processing workflow."""
        try:
            self.setup_driver()
            self.navigate_to_url()
            self.search_news()
            self.sort_news()
            self.extract_data()
            self.check_contains_money()
            self.count_search_phrase()
            self.download_picture()
            self.export_excel()
        finally:
            self.close_driver()

if __name__ == "__main__":
    logging.basicConfig(filename='output/log/news_extractor.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create an instance of NewsExtractor and execute the workflow
    news_extractor = NewsExtractor()
    
    # Execute the workflow
    news_extractor.run()