import streamlit as st
import pandas as pd
import requests
from src.config.api_keys import NEWS_API_KEY

st.set_page_config(layout="wide")
conn = st.connection("postgresql", type="sql")

def fetch_symbol_data(symbol):
    query = f'SELECT * FROM nasdaq_kpis WHERE "Symbol" = \'{symbol.upper()}\''
    result = conn.query(query) 
    return result

def fetch_symbol_history(symbol):
    query = f'SELECT "Date", "Close" FROM history_table WHERE "Symbol" = \'{symbol.upper()}\' ORDER BY "Date" ASC'
    result = conn.query(query) 
    return result

def fetch_symbol_price(symbol):
    query = f'SELECT "Close" FROM history_table WHERE "Symbol" = \'{symbol.upper()}\' ORDER BY "Date" DESC LIMIT 1'
    result = conn.query(query) 
    return result

def fetch_news(symbol):
    api_key = NEWS_API_KEY 
    url = f'https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['articles']
    else:
        st.error("Error fetching news.")
        return []

# Main Streamlit app
def main():
    st.title("Stock Symbol Details")
    symbol = st.text_input("Enter the stock symbol (e.g., AAPL):")

    if st.button("Search"):
        if symbol:
            data = fetch_symbol_data(symbol.upper())
            df = pd.DataFrame(data)
            
            price_data = fetch_symbol_price(symbol.upper())
            if price_data is not None:
                current_price = round(price_data['Close'], 2).iloc[0]
                st.markdown(
                    f"<h2 style='font-size: 24px; color: #ffffff;'>Current Price of {symbol.upper()}: <strong>${current_price}</strong></h2>",
                    unsafe_allow_html=True
    )

            data_hs = fetch_symbol_history(symbol.upper())

            historical_df = pd.DataFrame(data_hs)

            st.subheader(f"Historical Close Prices for {symbol.upper()}")

            historical_df['Date'] = pd.to_datetime(historical_df['Date'])
            historical_df.set_index('Date', inplace=True)

            st.line_chart(historical_df['Close'], use_container_width=True)


            excluded_fields = ['Name', 'Country', 'Website', 'Industry', 'Sector', 'Description', 'Symbol', 'Employees']
            
            df_filtered = df.drop(columns=excluded_fields)
            fields = {col: df_filtered[col].iloc[0] for col in df_filtered.columns}
            
            col_count = 13
            rows = list(fields.items())
            matrix_rows = [rows[i:i + col_count] for i in range(0, len(rows), col_count)]
            
            box_width = "114px"
            box_height = "82px"

            for row in matrix_rows:
                cols = st.columns(col_count)
                for (field_name, field_value), col in zip(row, cols):
                    col.markdown(
                        f"""
                        <div style="
                            display: flex; 
                            flex-direction: column; 
                            align-items: center; 
                            justify-content: center; 
                            background-color: #2e2e2e; 
                            width: {box_width}; 
                            height: {box_height}; 
                            padding: 8px; 
                            margin: 4px; 
                            border-radius: 5px;
                            font-size: 13px; 
                            color: #FFFFFF;
                        ">
                            <span style="color: #FFFFFF; font-weight: normal; text-align: center; font-size: 13px;">
                                {field_name.replace('_', ' ').title()}
                            </span>
                            <span style="color: #a8a8a8; font-weight: bold; font-size: 15px;">
                                {field_value if field_value is not None else '--'}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("---")

            st.subheader("Latest News")
            news_articles = fetch_news(symbol.upper())
            if news_articles:
                col_count = 3  
                cols = st.columns(col_count)

                valid_articles_count = 0

                for i, article in enumerate(news_articles): 
                    if article.get('description'):
                        col = cols[valid_articles_count % col_count]  
                        with col:
                            # Mostrar la imagen, si existe
                            if 'urlToImage' in article and article['urlToImage']:
                                st.image(article['urlToImage'], use_column_width=True)
                            st.markdown(f"**[{article['title']}]({article['url']})**")
                            st.write(article['description'])
                            st.write(f"*Published on {article['publishedAt']}*")
                            st.markdown("---")
                        valid_articles_count += 1  
                        
                        if valid_articles_count >= 9:
                            break
                else:
                    if len(news_articles) > 9:
                        article = news_articles[9]
                        col = cols[valid_articles_count % col_count]
                        with col:
                            if 'urlToImage' in article and article['urlToImage']:
                                st.image(article['urlToImage'], use_column_width=True)
                            st.markdown(f"**[{article['title']}]({article['url']})**")
                            st.write(article['description'])
                            st.write(f"*Published on {article['publishedAt']}*")
                            st.markdown("---")
            else:
                st.write("No news articles found.")
        else:
            st.warning("Please enter a stock symbol.")

if __name__ == "__main__":
    main()
