''' This script fetches and loads data from NASDAQ. '''
import os
import time
import glob
from botocore.exceptions import ClientError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.s3_connection import s3_client
from utils.selenium_options import selenium_options


class NasdaqSymbolsFetcher:
    ''' Class to fetch and load data from NASDAQ Website. '''

    def __init__(self):
        self.url = "https://www.nasdaq.com/market-activity/stocks/screener?page=1&exchange=NASDAQ&rows_per_page=1/"
        self.driver = webdriver.Chrome(options=selenium_options())
        self.s3 = s3_client()

    def download_nasdaq_symbols(self):
        ''' This function will download the CSV file from the URL and save it in the current directory. '''
        try:
            self.driver.get(self.url)
            time.sleep(5) 

            download_csv_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, 
                 '/html/body/div[2]/div/main/div[2]/article/div/div[1]/div[2]/div/div/div/div/div/div/div[2]/div[2]/div[3]/button')
                 ))
            
            download_csv_button.click()
            time.sleep(5) 

            self.driver.quit() # Close the browser
            return

        except Exception as e:
            print(f"An error occurred: {e}")
            return

    def upload_nasdaq_symbols_to_minio(self):
        ''' This function will upload the downloaded CSV to MinIO and then remove the local one.'''

        local_csv = glob.glob(os.path.join(os.getcwd(), '*.csv')) # Get our local CSV file
        if not local_csv:
            print("No CSV file found!")
            return

        try:
            self.s3.upload_file(local_csv[0], 'data', 'raw_data/nasdaq_symbols.csv')  # Upload the CSV to MinIO
            print("File uploaded to MinIO successfully!")

        except ClientError as e:
            print(f"Error uploading to MinIO: {e}")
            return

        finally:
            if os.path.exists(local_csv[0]):
                os.remove(local_csv[0]) # Clean up the local file
                return


if __name__ == "__main__":
    nasdaq = NasdaqSymbolsFetcher()
    nasdaq.download_nasdaq_symbols()
    nasdaq.upload_nasdaq_symbols_to_minio()
