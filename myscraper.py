import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

def scrape_search_results(brand_name):
    driver = webdriver.Chrome()
    driver.get(f'https://www.google.com/search?q={brand_name}')

    wait = WebDriverWait(driver, 20)

    products = []
    sources = []
    related_questions = []  # To store related questions
    additional_info = []  # To store additional information

    try:
        while len(products) < 10:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.g')))
            except TimeoutException:
                print(f"Timeout: Search results not present within the specified time for the brand: {brand_name}")
                break

            content = driver.page_source
            soup = BeautifulSoup(content, 'html.parser')

            for result in soup.select('div.g')[:10]:  # Limit to 10 results
                name = result.select_one('h3')
                if name:
                    products.append(name.text)
    
                    # Extracting the link with error handling
                    link = result.select_one('a')
                    if link and 'href' in link.attrs:
                        sources.append(link['href'])
                    else:
                        sources.append('N/A')

            # Wait for the related questions to be visible
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[jsname="yEVEwb"]')))

            # Extract related questions
            for question in soup.select('div[jsname="yEVEwb"]'):
                related_questions.append(question.text)

            # Extract additional information
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.k8XOCe.R0xfCb.VCOFK.s8bAkb')))
            for info_div in soup.select('a.k8XOCe.R0xfCb.VCOFK.s8bAkb'):
                additional_info.append(info_div.text.strip())

            try:
                next_button = driver.find_element(By.ID, 'pnnext')
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
        df = pd.DataFrame({'Product Name': products, 'Source': sources})
        related_questions_df = pd.DataFrame({'Related Questions': related_questions})  # Creating DataFrame for related questions
        additional_info_df = pd.DataFrame({'Additional Info': additional_info})  # Creating DataFrame for additional information

        # Save data to separate sheets in an Excel file
        excel_filename = f'{brand_name}_search_results.xlsx'
        with pd.ExcelWriter(excel_filename) as writer:
            df.to_excel(writer, sheet_name='Search Results', index=False)
            related_questions_df.to_excel(writer, sheet_name='Related Questions', index=False)
            additional_info_df.to_excel(writer, sheet_name='Additional Info', index=False)

        driver.quit()

        return excel_filename