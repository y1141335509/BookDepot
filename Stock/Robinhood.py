import robin_stocks.robinhood as r
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
username = os.getenv('ROBINHOOD_USERNAME')
password = os.getenv('ROBINHOOD_PASSWORD')
r.login(username, password)

# List of stock symbols to fetch data for
stock_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]  # Add more symbols as needed

if __name__ == '__main__':

    # Initialize an empty list to store the data
    all_stocks_data_list = []

    # Fetch and store historical data for each stock
    for symbol in stock_symbols:
        historical_data = r.stocks.get_stock_historicals(
            symbol,
            interval="day",
            span="year"
        )
        if historical_data:
            df = pd.DataFrame(historical_data)
            df['symbol'] = symbol  # Add a column for the stock symbol
            all_stocks_data_list.append(df)

    # Concatenate all DataFrames in the list into a single DataFrame
    if all_stocks_data_list:
        all_stocks_data = pd.concat(all_stocks_data_list, ignore_index=True)
        # Save the DataFrame to a CSV file
        all_stocks_data.to_csv("all_stocks_data.csv", index=False)
        print("Stock data saved to all_stocks_data.csv")
    else:
        print("No data was fetched.")

    # Logout from Robinhood
    r.logout()

    print("Stock data saved to all_stocks_data.csv")
