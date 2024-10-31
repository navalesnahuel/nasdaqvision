import psycopg2
from jobs.config.security_variables import PGUSER, PGPASSWORD, PGHOST, PGPORT

def PostgresConnection():
    try:
        connection = psycopg2.connect(
            dbname='platform',
            user=PGUSER,
            password=PGPASSWORD,
            host=PGHOST,
            port=PGPORT
        )

        return connection
    
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None