import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 加载 .env 文件中的凭据
load_dotenv()

# 数据库连接详细信息
db_config = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_CRATEJOY_DB")
}

# Cratejoy API 详细信息
cratejoy_base_url = "https://api.cratejoy.com/v1/"
client_id = os.getenv("CRATEJOY_CLIENT_ID")
secret_key = os.getenv("CRATEJOY_SECRET_KEY")

# 通用函数，用于获取 Cratejoy API 数据，支持分页处理
def get_cratejoy_data(endpoint):
    start_url = f"{cratejoy_base_url}{endpoint}"
    all_results, next_url = [], start_url
    while next_url:
        response = requests.get(next_url, auth=(client_id, secret_key))
        response.raise_for_status()
        data = response.json()

        # 将当前页的数据添加到结果列表中
        all_results.extend(data.get('results', []))

        # 获取下一页的 URL，如果存在则继续请求
        next_param = data.get('next')
        if next_param:
            if not next_param.startswith('http'):
                # 如果 next 是相对路径，拼接完整的 URL
                next_url = f"{start_url.rstrip('/')}/{next_param.lstrip('/')}"
            print('current url: ', next_url)
        else:
            # 如果没有下一页，停止循环
            break

    return all_results


# 获取所有 subscriptions 数据
subscriptions_data = get_cratejoy_data("subscriptions/")
# 获取所有 customers 数据
customers_data = get_cratejoy_data("customers/")
# 你还可以获取 products 或 orders 数据
products_data = get_cratejoy_data("products/")
orders_data = get_cratejoy_data("orders/")
inventory_data = get_cratejoy_data("inventory/")
transaction_data = get_cratejoy_data("transactions/")
shipment_data = get_cratejoy_data("shipments/")


# 将数据转换为 pandas DataFrames
subscriptions_df = pd.json_normalize(subscriptions_data)
customers_df = pd.json_normalize(customers_data)
products_df = pd.json_normalize(products_data)
orders_df = pd.json_normalize(orders_data)
inventory_df = pd.json_normalize(inventory_data)
transactions_df = pd.json_normalize(transaction_data)
shipment_df = pd.json_normalize(shipment_data)


# 如果需要进一步处理 subscriptions 数据中的嵌套字段，可以使用以下方法
def convert_lists_to_strings(df):
    for column in df.columns:
        if isinstance(df[column].iloc[0], list):
            df[column] = df[column].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)
    return df


subscriptions_df = convert_lists_to_strings(subscriptions_df)
products_df = convert_lists_to_strings(products_df)
orders_df = convert_lists_to_strings(orders_df)
inventory_df = convert_lists_to_strings(inventory_df)
transactions_df = convert_lists_to_strings(transactions_df)
shipment_df = convert_lists_to_strings(shipment_df)


# 准备 customer_subscriptions DataFrame，提取相关数据
customer_subscriptions_df = subscriptions_df[['id', 'customer.id']].rename(columns={'id': 'subscription_id', 'customer.id': 'customer_id'})

# 删除 subscriptions_df 中的复杂嵌套字段
columns_to_drop = ['address', 'billing', 'customer', 'product', 'product_instance', 'term']
subscriptions_df = subscriptions_df.drop(columns=columns_to_drop, errors='ignore')

# 连接到 MySQL 数据库并写入表中
engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

# 将 DataFrames 写入 MySQL 表
customers_df.to_sql('CUSTOMERS', engine, if_exists='replace', index=False)
subscriptions_df.to_sql('SUBSCRIPTIONS', engine, if_exists='replace', index=False)
customer_subscriptions_df.to_sql('CUSTOMER_SUBSCRIPTIONS', engine, if_exists='replace', index=False)

products_df.to_sql('PRODUCTS', engine, if_exists='replace', index=False)
orders_df.to_sql('ORDERS', engine, if_exists='replace', index=False)
inventory_df.to_sql('INVENTORY', engine, if_exists='replace', index=False)
transactions_df.to_sql('TRANSACTIONS', engine, if_exists='replace', index=False)
shipment_df.to_sql('SHIPMENTS', engine, if_exists='replace', index=False)


print("所有数据已成功从 Cratejoy 获取并写入 MySQL！")
