from jobs.utils.postgres_connection import PostgresConnection

def postgres_creation():
    # Create the PostgreSQL connection
    conn = PostgresConnection()

    try:
        # Ensure the connection was successful
        if conn is not None:
            cur = conn.cursor()

            # Create the nasdaq_kpis table if it doesn't exist
            try:
                cur.execute('''CREATE TABLE IF NOT EXISTS nasdaq_kpis (
                    symbol VARCHAR(10) NOT NULL,
                    name VARCHAR(255),
                    country VARCHAR(100),
                    website VARCHAR(255),
                    industry VARCHAR(100),
                    sector VARCHAR(100),
                    description TEXT,
                    employees INTEGER,
                    market_capitalization BIGINT,
                    total_revenue BIGINT,
                    net_income BIGINT,
                    eps_trailing DOUBLE PRECISION,
                    eps_forward DOUBLE PRECISION,
                    gross_margin DOUBLE PRECISION,
                    operating_margin DOUBLE PRECISION,
                    profit_margin DOUBLE PRECISION,
                    total_debt BIGINT,
                    enterprise_value BIGINT,
                    return_on_assets DOUBLE PRECISION,
                    return_on_equity DOUBLE PRECISION,
                    pe_ratio_trailing DOUBLE PRECISION,
                    pe_ratio_forward DOUBLE PRECISION,
                    beta DOUBLE PRECISION,
                    dividend_rate DOUBLE PRECISION,
                    dividend_yield DOUBLE PRECISION,
                    regular_market_previous_close DOUBLE PRECISION,
                    fifty_day_moving_average DOUBLE PRECISION,
                    two_hundred_day_moving_average DOUBLE PRECISION,
                    previous_close DOUBLE PRECISION,
                    audit_risk DOUBLE PRECISION,
                    board_risk DOUBLE PRECISION,
                    compensation_risk DOUBLE PRECISION,
                    shareholder_rights_risk DOUBLE PRECISION,
                    overall_risk DOUBLE PRECISION,
                    PRIMARY KEY (symbol)
                );''')
                print("nasdaq_kpis table created or already exists.")

            except Exception as e:
                print(f"Error creating nasdaq_kpis table: {e}")

            # Create the history_table with partitioning
            try:
                cur.execute('''CREATE TABLE IF NOT EXISTS history_table (
                    date TEXT,
                    open DOUBLE PRECISION,
                    high DOUBLE PRECISION,
                    low DOUBLE PRECISION,
                    close DOUBLE PRECISION,
                    volume BIGINT,
                    dividends DOUBLE PRECISION,
                    stock_splits DOUBLE PRECISION,
                    symbol VARCHAR(10) NOT NULL
                ) PARTITION BY LIST (symbol);''')
                print("history_table created or already exists.")

            except Exception as e:
                print(f"Error creating history_table: {e}")

            # Create an index on the symbol column for faster querying
            try:
                cur.execute('CREATE INDEX IF NOT EXISTS idx_symbol ON history_table (symbol);')
                print("Index idx_symbol created or already exists.")

            except Exception as e:
                print(f"Error creating index: {e}")

            # Commit the changes to the database
            conn.commit()
            print("Changes committed.")

        else:
            print("Failed to connect to the database.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if cur:
            cur.close()
            print("Cursor closed.")
        if conn:
            conn.close()
            print("Database connection closed.")