# News Extractor

The **News Extractor** is a Python script designed to extract news data from a specified website using Selenium, perform various operations on the data, and export the results to an Excel file. This script can be customized through a configuration file in `.ini` format to set parameters such as search phrase, section, date range, and more.

## Features

- **Selenium Automation:** Utilizes the Selenium library to automate interactions with a website, including search operations and date range filtering.
  
- **Data Extraction:** Extracts news data such as title, date, description, and picture source from the search results.

- **Picture Download:** Downloads pictures associated with the extracted news and saves them in the "output" directory.

- **Sorting and Filtering:** Allows sorting the search results based on criteria such as date and section.

- **Data Analysis:** Performs analysis on the extracted news data, checking for money-related information in titles and descriptions.

- **Excel Export:** Exports the processed news data to an Excel file with additional information such as picture filenames, search phrase occurrences, and money-related content indication.

## Setup

1. Install the required Python packages using the following command:

    ```
    pip install -r requirements.txt
    ```

2. Ensure you have the Chrome browser installed on your machine.

3. Update the `config.ini` file with your desired configuration parameters.

4. Run the script:

    ```
    python news_extractor.py
    ```

## Configuration

The script can be configured by modifying the `config.ini` file. Here's an example of the configuration file:

```ini
[Variables]
; The URL of the website to scrape
url = https://www.nytimes.com/

; The search phrase to be used for news extraction
search_phrase = Lakers

; The section of the news to filter
section = Sport

; Type of date range to consider
date_type = Specific Dates

; Number of months to consider in the search 
; (e.g., 0 or 1 - only the current month, 2 - current and previous month, 3 - current and two previous months, and so on)
months = 2

; Number of additional pages to load (e.g., set to 1 to extract 20 news, each page contains 10 news)
show_more = 1

[Paths]

; Path to the output Excel file
output_excel = output/excel/news_data.xlsx

; Path to the directory where pictures will be saved
picture_output = output/pictures/
```
## Logging

The script logs errors to the 'output/news_extractor.log' file for debugging purposes. Adjust the logging level as needed.

## Output

The script exports the processed news data to an Excel file located at 'output/news_data.xlsx'.

## Notes

Ensure proper web driver compatibility (currently configured for Chrome) and update chromedriver accordingly.

Customize the script as needed for the specific website structure and search functionality.

Note: This README assumes basic knowledge of Python and web scraping using Selenium. Please refer to the respective documentation for detailed information.
