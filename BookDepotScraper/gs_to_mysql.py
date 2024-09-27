import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from mysql.connector import connect, Error
from dotenv import load_dotenv

load_dotenv()


def fetch_google_sheets_data(sheet_id, range_name, creds_json):
    """Fetch data from Google Sheets"""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(creds_json, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(range_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df


def connect_to_mysql(user, password, host):
    """Connect to MySQL server"""
    try:
        conn = connect(
            user=user,
            password=password,
            host=host
        )
        return conn
    except Error as e:
        print(e)


def ensure_database_and_table(conn):
    """Ensure the database and table exist and recreate the table"""
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS BookDepot")
    cursor.execute("USE BookDepot")

    cursor.execute("DROP TABLE IF EXISTS BOOKS_PURCHASED")
    cursor.execute("""
        CREATE TABLE BOOKS_PURCHASED (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            ISBN VARCHAR(255) NULL,
            GENRE VARCHAR(255) NULL,
            BOOK_TITLE VARCHAR(255) NULL,
            AUTHORS VARCHAR(255) NULL,
            MONTH VARCHAR(255) NULL,
            YEAR INT NULL,
            PURCHASE_PRICE DECIMAL(10, 2) NULL,
            COUNT_TO_BUY INT NULL,
            BOOK_URL TEXT NULL,
            PURCHASE_QUANTITY INT NULL
        )
    """)
    conn.commit()
    cursor.close()


def clean_data(df):
    """Clean data before inserting into MySQL"""
    # Remove dollar sign from PURCHASE_PRICE and convert to float
    df['PURCHASE_PRICE'] = df['PURCHASE_PRICE'].replace('[\$,]', '', regex=True)
    df['PURCHASE_PRICE'] = df['PURCHASE_PRICE'].replace('', '0')
    df['PURCHASE_PRICE'] = df['PURCHASE_PRICE'].astype(float)

    # Handle empty ISBN values
    df['ISBN'] = df['ISBN'].replace('', None)

    # Handle empty COUNT_TO_BUY values
    df['COUNT_TO_BUY'] = df['COUNT_TO_BUY'].replace('', '0')
    df['COUNT_TO_BUY'] = df['COUNT_TO_BUY'].astype(int)

    # Handle empty PURCHASE_QUANTITY values
    df['PURCHASE_QUANTITY'] = df['PURCHASE_QUANTITY'].replace('', '0')
    df['PURCHASE_QUANTITY'] = df['PURCHASE_QUANTITY'].astype(int)

    return df


def insert_data_to_mysql(dataframe, conn):
    """Insert data into MySQL"""
    cursor = conn.cursor()
    # 打印列名和行数据，检查是否所有数据都正确加载并传递
    print("DataFrame Columns:", dataframe.columns)
    for _, row in dataframe.iterrows():
        cursor.execute("""
            INSERT INTO BOOKS_PURCHASED (
                ISBN, GENRE, BOOK_TITLE, AUTHORS, MONTH, YEAR, 
                PURCHASE_PRICE, COUNT_TO_BUY, BOOK_URL, PURCHASE_QUANTITY)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row.get('ISBN'), row.get('GENRE'), row.get('BOOK_TITLE'), row.get('AUTHORS'), row.get('MONTH'),
            row.get('YEAR'),
            row.get('PURCHASE_PRICE'), row.get('COUNT_TO_BUY'), row.get('BOOK_URL'), row.get('PURCHASE_QUANTITY')
        ))
    conn.commit()
    cursor.close()


def main():
    # Google Sheets settings
    GOOGLE_SHEETS_ID = '1UlbMqsK0LkasETKOgwWD5up9xxRBCg7dXgRTS6OTVJQ'  # Google Sheets ID
    RANGE_NAME = 'books'  # Worksheet name
    CREDS_JSON = 'credentials.json'  # Path to the service account key file

    # MySQL settings
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_DATABASE = 'BookDepot'

    # Fetch data from Google Sheets
    google_sheets_data = fetch_google_sheets_data(GOOGLE_SHEETS_ID, RANGE_NAME, CREDS_JSON)

    # 只保留需要的列并重命名
    columns_to_keep = {
        'ISBN': 'ISBN',
        'Genre': 'GENRE',
        'Book Title': 'BOOK_TITLE',
        'Authors': 'AUTHORS',
        'Month': 'MONTH',
        'Year': 'YEAR',
        'Purchase Price': 'PURCHASE_PRICE',
        'Count to Buy': 'COUNT_TO_BUY',
        'Book Url': 'BOOK_URL',
        'Purchase Quantity': 'PURCHASE_QUANTITY'
    }
    google_sheets_data = google_sheets_data[list(columns_to_keep.keys())]
    google_sheets_data = google_sheets_data.rename(columns=columns_to_keep)

    # Clean the data
    google_sheets_data = clean_data(google_sheets_data)

    # Connect to MySQL
    conn = connect_to_mysql(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST)

    # Ensure the database and table exist
    ensure_database_and_table(conn)

    # Insert data to MySQL
    insert_data_to_mysql(google_sheets_data, conn)

    # Close MySQL connection
    conn.close()


if __name__ == '__main__':
    main()
