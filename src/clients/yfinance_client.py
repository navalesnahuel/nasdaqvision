''' This script fetches and loads data from Yahoo Finance. '''
import io
import time
import concurrent.futures
import pandas as pd
import yfinance as yf
from jobs.utils.s3_connection import s3_client
import pyarrow as pa
import pyarrow.parquet as pq

class YFinanceClient:
    ''' This class fetches and loads data from Yahoo Finance. '''

    def __init__(self): 
        self.s3 = s3_client()
        # Load ticker symbols from S3 and store them in a list
        obj = self.s3.get_object(Bucket='data', Key='raw_data/nasdaq_symbols.csv')
        readeable_obj = io.BytesIO(obj['Body'].read())
        df_symbols = pd.read_csv(readeable_obj, index_col=False)

        # Symbol List for KPIS
        self.symbol_list = list(df_symbols[['symbol', 'name', 'country', 'sector', 'industry']]
                                .dropna().astype(str).itertuples(index=False, name=None))
        
        # Symbol List for Historical KPIs
        self.symbol_hist_list = list(df_symbols['symbol'].dropna().astype(str))

    def get_company_kpis(self, symbol, name, country, sector, industry): 
        ''' Fetches KPIs from Yahoo Finance. '''
        try:
            info = yf.Ticker(symbol).info # Get information from Ticker

            return {

                'Symbol': symbol,
                'Name': name,
                'Country': country,
                'Website': info.get('website'),
                'Industry': industry,
                'Sector': sector,
                'Description': info.get('longBusinessSummary'),
                'Employees': info.get('fullTimeEmployees'),
                'Market_Capitalization': info.get('marketCap'),
                'Total_Revenue': info.get('totalRevenue'),
                'Net_Income': info.get('netIncomeToCommon'),
                'EPS_Trailing': info.get('trailingEps'),
                'EPS_Forward': info.get('forwardEps'),
                'Gross_Margin': info.get('grossMargins'),
                'Operating_Margin': info.get('operatingMargins'),
                'Profit_Margin': info.get('profitMargins'),
                'Total_Debt': info.get('totalDebt'),
                'Enterprise_Value': info.get('enterpriseValue'),
                'Return_on_Assets': info.get('returnOnAssets'),
                'Return_on_Equity': info.get('returnOnEquity'),
                'PE_Ratio_Trailing': info.get('trailingPE'),
                'PE_Ratio_Forward': info.get('forwardPE'),
                'Beta': info.get('beta'),
                'Dividend_Rate': info.get('dividendRate'),
                'Dividend_Yield': info.get('dividendYield'),
                'Regular_Market_Previous_Close': info.get('regularMarketPreviousClose'),
                '50-Day_Moving_Average': info.get('fiftyDayAverage'),
                '200-Day_Moving_Average': info.get('twoHundredDayAverage'),
                'Previous_Close': info.get('previousClose'),
                'Audit_Risk': info.get('auditRisk'),
                'Board_Risk': info.get('boardRisk'),
                'Compensation_Risk': info.get('compensationRisk'),
                'Shareholder_Rights_Risk': info.get('shareHolderRightsRisk'),
                'Overall_Risk': info.get('overallRisk')
            }

        except Exception as error:
            print(f"Error at {symbol}, {name}: {error}")
            return None

    def assets_to_csv(self, dictlist): 
        ''' Dictionary list to CSV. '''
        df_assets = pd.DataFrame(dictlist)

        with io.StringIO() as csv_buffer:
            df_assets.to_csv(csv_buffer, index=False)

            response = self.s3.put_object(
                Bucket='data', 
                Key="raw_data/assets.csv", 
                Body=csv_buffer.getvalue()
                )

            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

            if status == 200:
                print(f"Successful S3 put_object response. Status - {status}")
            else:
                print(f"Unsuccessful put_object response. Status - {status}, Response: {response}")

    def threading_kpis(self): 
        ''' Threading for `get_company_kpis` '''
        dictlist = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.get_company_kpis, symbol, name, country, sector, industry) \
                        for symbol, name, country, sector, industry in self.symbol_list}

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    dictlist.append(result)

        self.assets_to_csv(dictlist)

    def get_historical_kpis(self, symbol): 
        ''' Fetch Historical KPIS for every NASDAQ company'''
        periods = ['1d', '5d','max']

        try:
            ticker = yf.Ticker(symbol)
            # Fetch Historical data from Yfinance.
            hist = None
            for period in periods[::-1]:
                hist = ticker.history(period=period)
                if not hist.empty:
                    print(f"Successfully fetched {period} period for {symbol}.")
                    break
            else:
                print(f"No data found for {symbol} in any period.")
                return None
            
            # Conver to a dataframe and add symbol
            hist_df = pd.DataFrame(hist).reset_index()
            hist_df['Symbol'] = symbol
            hist_df['Date'] = hist_df['Date'].astype(str)

            # Write to S3 as a parquet
            table = pa.Table.from_pandas(hist_df)
            with io.BytesIO() as out_buffer:
                pq.write_table(table, out_buffer)
                out_buffer.seek(0)
                self.s3.put_object(Body=out_buffer, Bucket='data', Key=f'tickers/{symbol}/{symbol}.parquet')

                    
        except Exception as error:
            print(f"Error at {symbol}: {error}")

    def threading_historical_kpis(self):
        ''' Threading for `get_historical_kpis` '''
        with concurrent.futures.ThreadPoolExecutor() as executor:
            [executor.submit(self.get_historical_kpis, symbol) for symbol in self.symbol_hist_list]

if __name__ == "__main__":

    client = YFinanceClient()
    start = time.time()

    client.threading_kpis()
    client.threading_historical_kpis()

    end = time.time()
    
    print("It took ", end - start, " seconds!")


