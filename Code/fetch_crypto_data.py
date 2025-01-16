import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import pandas as pd
import datetime
import schedule
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Google Sheets API setup
scope = ["your spreadsheet", "your google sheet api"] # Replace with your actual Google Sheet API
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)

# Google Sheet ID
sheet_id = "spreadsheet ID"  # Replace with your actual Google Sheet ID

# Open the Google Sheet
try:
    logging.info("Connecting to Google Sheet...")
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.get_worksheet(0)  # First worksheet
    logging.info("Successfully connected to Google Sheet.")
except Exception as e:
    logging.error(f"Error connecting to Google Sheet: {e}")
    exit()

# Test writing to the sheet
try:
    logging.info("Writing test data to the sheet...")
    worksheet.update_cell(1, 1, "Test Write")  # Write "Test Write" to cell A1
    logging.info("Test data written successfully.")
except Exception as e:
    logging.error(f"Error writing test data to the sheet: {e}")
    exit()

# API endpoint and parameters
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",              # Currency for prices
    "order": "market_cap_desc",        # Order by market cap
    "per_page": 50,                    # Top 50 results
    "page": 1,                         # First page
    "sparkline": False                 # No sparkline data needed
}

# Function to fetch data and update Google Sheet
def fetch_and_update_sheet():
    try:
        # Fetch data from API
        response = requests.get(url, params=params)
        if response.status_code == 200:
            logging.info("Fetching cryptocurrency data from API...")
            data = response.json()
            df = pd.DataFrame(data)

            # Prepare data for Google Sheets
            df['Last Updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            headers = ["Cryptocurrency Name", "Symbol", "Current Price (in USD)", "Market Cap", "24-hour Trading Volume", "24-hour Change (%)", "Last Updated"]
            rows = df[["name", "symbol", "current_price", "market_cap", "total_volume", "price_change_percentage_24h", "Last Updated"]].values.tolist()

            # Clear existing data in the sheet
            logging.info("Clearing old data in the sheet...")
            worksheet.clear()

            # Update Google Sheet with new data
            logging.info("Writing new data to the sheet...")
            worksheet.append_row(headers)
            worksheet.append_rows(rows)
            logging.info("Sheet updated successfully.")
        else:
            logging.error(f"Error fetching data from API. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"An error occurred while fetching or updating data: {e}")

# Initial run
fetch_and_update_sheet()

# Schedule updates every 5 minutes
schedule.every(5).minutes.do(fetch_and_update_sheet)

print("Live updates started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)
