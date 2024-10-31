from pyspark.sql import SparkSession
from pyspark.sql.functions import format_number
from jobs.config.security_variables import MINIO_ENDPOINT, MINIO_PASSWORD, MINIO_USER
from jobs.config.security_variables import PGUSER, PGPASSWORD

# Initialize Spark session
spark = SparkSession.builder \
    .master("spark://spark-master:7077") \
    .appName("LoadToWarehouse") \
    .enableHiveSupport() \
    .config("fs.s3a.access.key", MINIO_USER) \
    .config("fs.s3a.secret.key", MINIO_PASSWORD) \
    .config("fs.s3a.path.style.access", "true") \
    .config("fs.s3a.endpoint", MINIO_ENDPOINT) \
    .config("fs.s3a.connection.ssl.enabled", "false") \
    .config("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
    .config("spark.sql.catalogImplementation", "hive") \
    .config("spark.sql.warehouse.dir", "s3a://data/warehouse") \
    .getOrCreate()

# Database properties and JDBC URL
DB_PROPERTIES = {
    "user": PGUSER,
    "password": PGPASSWORD,
    "driver": 'org.postgresql.Driver'
}

JDBC = f'jdbc:postgresql://postgresql:5432/platform'

# Read assets CSV from S3
df_assets = spark.read.csv('s3a://data/raw_data/assets.csv', header=True, inferSchema=True)

# Define column types
string_columns = ['Symbol', 'Name', 'Country', 'Website', 'Industry', 'Sector', 'Description']
big_number_columns = ['Market_Capitalization', 'Total_Revenue', 'Net_Income', 'Total_Debt', 'Enterprise_Value']
double_columns = [
    'EPS_Trailing', 'EPS_Forward', 'Gross_Margin', 'Operating_Margin', 'Profit_Margin',
    'Return_on_Assets', 'Return_on_Equity', 'PE_Ratio_Trailing', 'PE_Ratio_Forward', 
    'Beta', 'Dividend_Rate', 'Dividend_Yield', 'Regular_Market_Previous_Close',
    '50-Day_Moving_Average', '200-Day_Moving_Average', 'Previous_Close',
    'Audit_Risk', 'Board_Risk', 'Compensation_Risk', 'Shareholder_Rights_Risk', 
    'Overall_Risk'
]

# Change data types and format numbers correctly
df_assets = df_assets.withColumn('Employees', df_assets['Employees'].cast('Integer'))

for column in string_columns:
    df_assets = df_assets.withColumn(column, df_assets[column].cast('String'))

for column in double_columns:
    df_assets = df_assets.withColumn(column, format_number(df_assets[column].cast('Double'), 2))

for column in big_number_columns:
    df_assets = df_assets.withColumn(column, format_number(df_assets[column].cast('Decimal'), 0))

# Write assets to PostgreSQL
df_assets.write \
    .mode('overwrite') \
    .jdbc(url=JDBC, table="nasdaq_kpis", properties=DB_PROPERTIES)

# Read historical data from S3 and write to another S3 path
df = spark.read.parquet("s3a://data/tickers/*/")
df.write.mode('overwrite').parquet("s3a://data/raw_data/history_table/")

# Read historical table from S3 and write to PostgreSQL
df_history_table = spark.read.parquet("s3a://data/raw_data/history_table/", header=True, inferSchema=True)
df_history_table.write \
    .mode('overwrite') \
    .jdbc(url=JDBC, table="history_table", properties=DB_PROPERTIES)

# Stop the Spark session
spark.stop()