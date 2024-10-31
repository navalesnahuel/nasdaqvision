''' This code loads the security variables from the .env file. '''
import os 
from dotenv import load_dotenv

load_dotenv('/opt/airflow/.env')

#MINIO
MINIO_ENDPOINT=os.getenv('MINIO_ENDPOINT')
MINIO_USER=os.getenv('MINIO_USER')
MINIO_PASSWORD=os.getenv('MINIO_PASSWORD')

# POSTGRES
PGUSER=os.getenv('PGUSER')
PGPASSWORD=os.getenv('PGPASSWORD')
PGHOST=os.getenv('PGHOST')
PGPORT=os.getenv('PGPORT')
PGDB=os.getenv('PGDB')

# SPARK
SPARK_MASTER=os.getenv('SPARK_MASTER')
