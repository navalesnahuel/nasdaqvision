''' This script fetches and loads data from NASDAQ. '''
import os
import glob
from botocore.exceptions import ClientError
from jobs.utils.s3_connection import s3_client
import requests
import pandas as pd

class NasdaqSymbolsFetcher:
    ''' Class to fetch and load data from NASDAQ Website. '''
    def __init__(self):
         self.s3 = s3_client()
         self.data_path = '/opt/airflow/jobs/'

    def download_nasdaq_data(self):
        '''Download Nasdaq Symbols'''
        
        api_url = "https://api.nasdaq.com/api/screener/stocks"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
        params = {
            'exchange': 'NASDAQ',
            'download': 'true',
            'rows': 100,
            'page': 1
        }
        
        try:
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data['data']['rows'])
            
            output_path = os.path.join(self.data_path, f'nasdaq_stocks.csv')
            
            df.to_csv(output_path, index=False)        
            
        except Exception as e:
            print(f"Error en la descarga de datos: {str(e)}")
            raise

    def upload_nasdaq_symbols_to_minio(self):
        ''' This function will upload the downloaded CSV to MinIO and then remove the local one.'''

        local_csv = glob.glob(os.path.join(self.data_path, '*.csv')) # Get our local CSV file
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
