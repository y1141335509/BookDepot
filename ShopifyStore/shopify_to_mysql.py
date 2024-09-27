import os
import pandas as pd
from mysql.connector import connect, Error
from dotenv import load_dotenv
import shopify
from Shopify import (
    initialize_session,
    get_orders,
    orders_to_dataframe,
    get_products,
    products_to_dataframe,
    get_collections,
    collections_to_dataframe,
    get_inventory_items,
    inventory_items_to_dataframe,
    get_fulfillments,
    fulfillments_to_dataframe,
    get_abandoned_checkouts,
    abandoned_checkouts_to_dataframe,
    get_price_rules,
    price_rules_to_dataframe,
    get_refunds,
    refunds_to_dataframe,
    get_shop_info,
    shop_info_to_dataframe
)

load_dotenv()

# MySQL settings
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_DATABASE = 'ShopifyStore'

def connect_to_mysql(user, password, host, database):
    """Connect to MySQL server"""
    try:
        conn = connect(
            user=user,
            password=password,
            host=host,
            database=database
        )
        return conn
    except Error as e:
        print(e)
        return None

def create_database_and_tables(conn):
    """Create database and tables"""
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
    cursor.execute(f"USE {MYSQL_DATABASE}")

    tables = {
        "ORDERS": """
            CREATE TABLE ORDERS (
                ID BIGINT AUTO_INCREMENT PRIMARY KEY,
                ORDER_ID BIGINT,
                ORDER_NUMBER VARCHAR(255),
                TOTAL_PRICE DECIMAL(10, 2),
                CREATED_AT DATETIME,
                FINANCIAL_STATUS VARCHAR(255),
                FULFILLMENT_STATUS VARCHAR(255),
                CUSTOMER_EMAIL VARCHAR(255),
                TOTAL_DISCOUNTS DECIMAL(10, 2),
                TOTAL_LINE_ITEMS_PRICE DECIMAL(10, 2),
                TOTAL_TAX DECIMAL(10, 2),
                TOTAL_WEIGHT BIGINT,
                CURRENCY VARCHAR(255)
            )
        """,
        "PRODUCTS": """
            CREATE TABLE PRODUCTS (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                PRODUCT_ID BIGINT,
                TITLE VARCHAR(255),
                VENDOR VARCHAR(255),
                PRODUCT_TYPE VARCHAR(255),
                CREATED_AT DATETIME,
                UPDATED_AT DATETIME,
                PUBLISHED_AT DATETIME,
                TAGS TEXT
            )
        """,
        "COLLECTIONS": """
            CREATE TABLE COLLECTIONS (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                COLLECTION_ID BIGINT,
                HANDLE VARCHAR(255),
                TITLE VARCHAR(255),
                UPDATED_AT DATETIME,
                PUBLISHED_AT DATETIME
            )
        """,
        "INVENTORY": """
            CREATE TABLE INVENTORY (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                INVENTORY_ITEM_ID BIGINT,
                SKU VARCHAR(255),
                CREATED_AT DATETIME,
                UPDATED_AT DATETIME,
                REQUIRES_SHIPPING BOOLEAN,
                COST DECIMAL(10, 2),
                COUNTRY_CODE_OF_ORIGIN VARCHAR(255)
            )
        """,
        "FULFILLMENT": """
            CREATE TABLE FULFILLMENT (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                FULFILLMENT_ID BIGINT,
                ORDER_ID BIGINT,
                STATUS VARCHAR(255),
                CREATED_AT DATETIME,
                UPDATED_AT DATETIME,
                TRACKING_COMPANY VARCHAR(255),
                TRACKING_NUMBER VARCHAR(255)
            )
        """,
        "ABANDONED_CHECKOUTS": """
            CREATE TABLE ABANDONED_CHECKOUTS (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                CHECKOUT_ID BIGINT,
                TOKEN VARCHAR(255),
                CART_TOKEN VARCHAR(255),
                EMAIL VARCHAR(255),
                CREATED_AT DATETIME,
                UPDATED_AT DATETIME,
                COMPLETED_AT DATETIME,
                TOTAL_PRICE DECIMAL(10, 2)
            )
        """,
        "DISCOUNTS": """
            CREATE TABLE DISCOUNTS (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                PRICE_RULE_ID BIGINT,
                TITLE VARCHAR(255),
                TARGET_TYPE VARCHAR(255),
                TARGET_SELECTION VARCHAR(255),
                ALLOCATION_METHOD VARCHAR(255),
                VALUE_TYPE VARCHAR(255),
                VALUE DECIMAL(10, 2),
                STARTS_AT DATETIME,
                ENDS_AT DATETIME
            )
        """,
        "REFUND": """
            CREATE TABLE REFUND (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                REFUND_ID BIGINT,
                ORDER_ID BIGINT,
                CREATED_AT DATETIME,
                NOTE TEXT,
                RESTOCK BOOLEAN
            )
        """,
        "STORE_INFORMATION": """
            CREATE TABLE STORE_INFORMATION (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                NAME VARCHAR(255),
                EMAIL VARCHAR(255),
                DOMAIN VARCHAR(255),
                PROVINCE VARCHAR(255),
                COUNTRY VARCHAR(255),
                ADDRESS1 VARCHAR(255),
                ZIP VARCHAR(255),
                CITY VARCHAR(255),
                SOURCE VARCHAR(255),
                PHONE VARCHAR(255),
                CREATED_AT DATETIME,
                UPDATED_AT DATETIME
            )
        """
    }

    for table_name, table_schema in tables.items():
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        cursor.execute(table_schema)

    conn.commit()
    cursor.close()

def insert_data_to_mysql(table_name, dataframe, conn):
    """Insert data into MySQL"""
    cursor = conn.cursor()
    cols = ", ".join([str(i).upper() for i in dataframe.columns.tolist()])
    for _, row in dataframe.iterrows():
        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({', '.join(['%s'] * len(row))})"
        cursor.execute(sql, tuple(row))
    conn.commit()
    cursor.close()

def main():
    initialize_session()

    conn = connect_to_mysql(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE)
    if conn is None:
        print("Failed to connect to MySQL.")
        return

    create_database_and_tables(conn)

    # Fetch data from Shopify and insert into MySQL
    orders = get_orders()
    orders_df = orders_to_dataframe(orders)
    insert_data_to_mysql("ORDERS", orders_df, conn)

    products = get_products()
    products_df = products_to_dataframe(products)
    insert_data_to_mysql("PRODUCTS", products_df, conn)

    collections = get_collections()
    collections_df = collections_to_dataframe(collections)
    insert_data_to_mysql("COLLECTIONS", collections_df, conn)

    inventory_items = get_inventory_items()
    inventory_items_df = inventory_items_to_dataframe(inventory_items)
    insert_data_to_mysql("INVENTORY", inventory_items_df, conn)

    fulfillments = []
    for order in orders:
        fulfillments.extend(get_fulfillments(order.id))
    fulfillments_df = fulfillments_to_dataframe(fulfillments)
    insert_data_to_mysql("FULFILLMENT", fulfillments_df, conn)

    abandoned_checkouts = get_abandoned_checkouts()
    abandoned_checkouts_df = abandoned_checkouts_to_dataframe(abandoned_checkouts)
    insert_data_to_mysql("ABANDONED_CHECKOUTS", abandoned_checkouts_df, conn)

    price_rules = get_price_rules()
    price_rules_df = price_rules_to_dataframe(price_rules)
    insert_data_to_mysql("DISCOUNTS", price_rules_df, conn)

    refunds = []
    for order in orders:
        refunds.extend(get_refunds(order.id))
    refunds_df = refunds_to_dataframe(refunds)
    insert_data_to_mysql("REFUND", refunds_df, conn)

    shop_info = get_shop_info()
    shop_info_df = shop_info_to_dataframe(shop_info)
    insert_data_to_mysql("STORE_INFORMATION", shop_info_df, conn)

    conn.close()
    print("Data export to MySQL complete.")


if __name__ == "__main__":
    main()
