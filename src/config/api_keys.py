''' This code loads the API keys from the .env file. '''
import os
from dotenv import load_dotenv

load_dotenv('/opt/airflow/.env')

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
