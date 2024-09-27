import os
import pandas as pd
from mysql.connector import connect, Error
from dotenv import load_dotenv

load_dotenv()


def load_data(filename):
    """Load data from CSV file."""
    return pd.read_csv(filename)


def split_size(size_str):
    """Extract length, width, and height from size string."""
    try:
        length, width, height = size_str.split(' x ')
        length = float(length.replace('" l', ''))
        width = float(width.replace('" w', ''))
        height = float(height.replace('"', ''))
        # print(f'Length: {length}, Width: {width}, Height: {height}')
        return length, width, height
    except:
        return None, None, None


def get_sales_price(price_str):
    """
    Extract sales price from price string.
    Explanation: the crawled price column looks like:
    |    price      |               |   price   |
    |$3.00 $1.50    |               |   $1.50   |
    |$2.75          |       ==>     |   $2.75   |
    |$2.00 $1.25    |               |   $1.25   |
    |$3.50          |               |   $3.50   |
    If there are 2 prices, it means there's a discount. Otherwise, no discount.
    We want to always keep the last price
    """
    if len(price_str) < 5:
        return price_str
    return price_str[-5:]


def clean_stock_quantity(stock_str):
    """
    Convert '1000+' to '1000'
    :param stock_str:
    :return: stock_quantity
    """
    if stock_str == '1000+':
        return int(1000)
    return int(stock_str)


def process_data(df, source='csv'):
    """Process the dataframe."""
    # Split size into length, width, height
    if 'size' in df.columns:
        df[['length', 'width', 'height']] = df['size'].apply(
            lambda x: pd.Series(split_size(x))
        )

    # Get the sales price on BookDepot.com:
    if 'price' in df.columns:
        df['sales_price'] = df['price'].apply(lambda x: pd.Series(get_sales_price(x)))

    # Clean stock quantity and convert stock quantity to Integer:
    if 'stock' in df.columns:
        df['stock_quantity'] = df['stock'].apply(lambda x: pd.Series(clean_stock_quantity(x)))

    # Convert publication date to datetime
    if 'publication_date' in df.columns:
        df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce', format='%Y-%m-%d')

    # Handle missing values or errors
    df.fillna({'length': 0, 'width': 0, 'height': 0}, inplace=True)

    columns_to_drop = ['size', 'list_price', 'price', 'stock']

    if source == 'csv':
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    return df


def clean_data(df):
    """Clean data before inserting into MySQL"""
    # Remove dollar sign from SALES_PRICE and convert to float
    df['sales_price'] = df['sales_price'].replace('[\$,+]', '', regex=True)
    df['sales_price'] = df['sales_price'].replace('', '0')
    df['sales_price'] = df['sales_price'].astype(float)

    # Handle empty ISBN values
    df['isbn'] = df['isbn'].replace('', None)

    # Replace NaN with None (to be inserted as NULL in MySQL)
    df = df.where(pd.notnull(df), None)

    return df



def save_data(df, filename):
    """Save the dataframe to a new CSV file."""
    df.to_csv(filename, index=False)


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

    cursor.execute("DROP TABLE IF EXISTS BOOKDEPOT_FICTION_ROMANCE")
    cursor.execute("""
        CREATE TABLE BOOKDEPOT_FICTION_ROMANCE (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ISBN VARCHAR(255) NULL,
            BOOK_TITLE VARCHAR(255) NULL,
            AUTHOR VARCHAR(255) NULL,
            STOCK_QUANTITY INT NULL,
            CATEGORIES TEXT NULL,
            LENGTH DECIMAL(10, 2) NULL,
            WIDTH DECIMAL(10, 2) NULL,
            HEIGHT DECIMAL(10, 2) NULL,
            SALES_PRICE DECIMAL(10, 2) NULL,
            PUBLISHER VARCHAR(255) NULL,
            BOOK_COVER TEXT NULL,
            BINDING VARCHAR(255) NULL,
            PUBLISH_DATE DATE NULL,
            URL VARCHAR(255) NULL
        )
    """)
    conn.commit()
    cursor.close()
    print('successfully re-created BOOKDEPOT_FICTION_ROMANCE')


def insert_data_to_mysql(dataframe, conn):
    """Insert data into MySQL"""
    cursor = conn.cursor()
    for _, row in dataframe.iterrows():
        cursor.execute("""
                INSERT INTO BOOKDEPOT_FICTION_ROMANCE (
                    ISBN, BOOK_TITLE, AUTHOR, STOCK_QUANTITY, CATEGORIES, LENGTH, WIDTH, HEIGHT, SALES_PRICE, PUBLISHER, 
                    BOOK_COVER, BINDING, PUBLISH_DATE, URL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
            row.get('isbn'), row.get('title'), row.get('author'), row.get('stock_quantity'), row.get('categories'),
            row.get('length'), row.get('width'), row.get('height'), row.get('sales_price'), row.get('publisher'),
            row.get('cover'), row.get('binding'), row.get('publication_date'), row.get('url')
        ))
    conn.commit()
    cursor.close()


def main():
    # Load the data
    data = load_data('output.csv')

    # Process the data
    processed_data = process_data(data)

    # Clean the data
    processed_data = clean_data(processed_data)

    # Save the cleaned data # 获取当前代码文件的所在目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_directory, 'cleaned_output.csv')
    save_data(processed_data, 'cleaned_output.csv')

    # MySQL settings
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_DATABASE = 'BookDepot'

    # Connect to MySQL
    conn = connect_to_mysql(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST)

    # Ensure the database and table exist
    ensure_database_and_table(conn)

    # Insert data to MySQL
    insert_data_to_mysql(processed_data, conn)

    # Close MySQL connection
    conn.close()


if __name__ == "__main__":
    main()

