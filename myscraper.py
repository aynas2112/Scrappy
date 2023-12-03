from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import os

def scrape_search_results(brand_name):
    driver = webdriver.Chrome()
    driver.get(f'https://www.bing.com/search?q={brand_name}')

    wait = WebDriverWait(driver, 20)
    action_chains = ActionChains(driver)

    products = []
    sources = []
    reviews = []
    ratings = []

    try:
        while True:
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'b_algo')))
            except TimeoutException:
                print(f"Timeout: Search results not present within the specified time for the brand: {brand_name}")
                break

            content = driver.page_source
            soup = BeautifulSoup(content, 'html.parser')

            for result in soup.find_all('li', {'class': 'b_algo'}):
                name = result.find('h2')
                snippet = result.find('div', {'class': 'b_caption'})
                rating = result.find('div', {'class': 'b_vPanel'})

                if name and snippet:
                    products.append(name.text)
                    reviews.append(snippet.text)

                    # Extracting the link with error handling
                    link = result.find('a')
                    if link and 'href' in link.attrs:
                        sources.append(link['href'])
                    else:
                        sources.append('N/A')

                if rating:
                    ratings.append(rating.text)
                else:
                    ratings.append('N/A')

            try:
                next_button = driver.find_element(By.CLASS_NAME, 'sb_pagN')
                action_chains.move_to_element(next_button).perform()
                driver.execute_script("arguments[0].click();", next_button)
            except TimeoutException:
                print("No more pages available.")
                break
            except KeyboardInterrupt:
                print("Scraping interrupted by user.")
                break

    except KeyboardInterrupt:
        print("Scraping interrupted by user.")
    finally:
        df = pd.DataFrame({'Product Name': products, 'Source': sources, 'Reviews': reviews, 'Ratings': ratings})
        csv_filename = f'{brand_name}_search_results.csv'
        xlsx_filename = f'{brand_name}_search_results.xlsx'

        # Save data to a CSV file
        df.to_csv(csv_filename, index=False)

        # Convert CSV to XLSX
        df.to_excel(xlsx_filename, index=False)

        # Clean up CSV file
        os.remove(csv_filename)

        driver.quit()

        return xlsx_filename
