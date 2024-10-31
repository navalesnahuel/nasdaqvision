import datetime
from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from jobs.clients.nasdaq_symbols import NasdaqSymbolsFetcher 
from jobs.clients.yfinance_client import YFinanceClient
from jobs.create_tables_postgres import postgres_creation

def fetch_nasdaq_data():
    ''' Fetch all the symbols from Nasdaq '''
    nasdaq = NasdaqSymbolsFetcher()
    nasdaq.download_nasdaq_data()
    nasdaq.upload_nasdaq_symbols_to_minio()

def fetch_yahoo_finance():
    ''' Fetch all the KPIs using the Nasdaq symbols '''
    yfinance = YFinanceClient()
    yfinance.threading_kpis()
    yfinance.threading_historical_kpis()


@dag(start_date=datetime.datetime(2021, 7, 30), 
     dag_id='nasdaqvision',
     schedule_interval="@daily", 
     catchup=False)

def sequential_spark_jobs():
    start = EmptyOperator(task_id='start')


    nasdaq = PythonOperator(
        task_id='nasdaq_fetch_csv',
        python_callable=fetch_nasdaq_data
    )

    yfinance_yahoo = PythonOperator(
        task_id='yfinance_get_symbols_data',
        python_callable=fetch_yahoo_finance
    )

    warehouse_tables = PythonOperator(
        task_id='warehouse_tables_creation',
        python_callable=postgres_creation
    )

    spark_job = SparkSubmitOperator(
        task_id='spark_transform_load_data_to_warehouse',
        application='jobs/load_to_psql.py',
        conn_id='spark_default',
        conf={'spark.jars': 'jars/hadoop-aws-3.3.4.jar,jars/antlr4-runtime-4.9.3.jar,jars/aws-java-sdk-bundle-1.12.262.jar, jars/postgresql-42.6.0.jar'},
        verbose=True
    )

    end = EmptyOperator(task_id='end')

    start >> nasdaq >> yfinance_yahoo >> warehouse_tables >> spark_job >> end


sequential_spark_jobs()