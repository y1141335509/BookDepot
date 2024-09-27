import time

import shopify
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get('SHOPIFY_API_KEY')
ACCESS_TOKEN = os.environ.get('SHOPIFY_ACCESS_TOKEN')
API_SECRET_KEY = os.environ.get('SHOPIFY_API_SECRET_KEY')
STORE_NAME = os.environ.get('SHOPIFY_STORE_NAME')

if not all([API_KEY, API_SECRET_KEY, ACCESS_TOKEN, STORE_NAME]):
    raise ValueError("Please set all required environment variables.")

SHOP_URL = f"https://{API_KEY}:{API_SECRET_KEY}@{STORE_NAME}.myshopify.com/admin/api/2023-10"
shopify.ShopifyResource.set_site(SHOP_URL)
shopify.Session.setup(api_key=API_KEY, secret=API_SECRET_KEY)


def initialize_session():
    session = shopify.Session(f"{STORE_NAME}.myshopify.com", "2023-10", ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)


def get_all_resources(resource_class, **kwargs):
    all_resources = []
    since_id = 0
    while True:
        resources = resource_class.find(limit=250, since_id=since_id, **kwargs)
        if not resources:
            break
        all_resources.extend(resources)
        print(f"Retrieved {len(resources)} {resource_class.__name__}")
        since_id = resources[-1].id
    print(f"Total {resource_class.__name__} retrieved: {len(all_resources)}")
    return all_resources


############################# ORDERS #############################
def get_orders():
    return get_all_resources(shopify.Order, status='any')


def orders_to_dataframe(orders):
    data = []
    for order in orders:
        customer_email = 'N/A'
        if hasattr(order, 'customer') and order.customer is not None:
            customer_email = getattr(order.customer, 'email', 'N/A')

        data.append({
            'id': order.id,
            'order_number': order.order_number,
            'total_price': order.total_price,
            'created_at': order.created_at,
            'financial_status': order.financial_status,
            'fulfillment_status': order.fulfillment_status,
            'customer_email': customer_email,
            'total_discounts': order.total_discounts,
            'total_line_items_price': order.total_line_items_price,
            'total_tax': order.total_tax,
            'total_weight': order.total_weight,
            'currency': order.currency,
        })
    return pd.DataFrame(data)
############################# ORDERS #############################


############################# PRODUCTS #############################
def get_products():
    return get_all_resources(shopify.Product)


def products_to_dataframe(products):
    data = []
    for product in products:
        data.append({
            'id': product.id,
            'title': product.title,
            'vendor': product.vendor,
            'product_type': product.product_type,
            'created_at': product.created_at,
            'updated_at': product.updated_at,
            'published_at': product.published_at,
            'tags': product.tags,
        })
    return pd.DataFrame(data)
############################# PRODUCTS #############################


############################# COLLECTIONS #############################
def get_collections():
    return get_all_resources(shopify.CustomCollection)


def collections_to_dataframe(collections):
    data = []
    for collection in collections:
        data.append({
            'id': collection.id,
            'handle': collection.handle,
            'title': collection.title,
            'updated_at': collection.updated_at,
            'published_at': collection.published_at,
        })
    return pd.DataFrame(data)
############################# COLLECTIONS #############################


############################# INVENTORY #############################
def inventory_levels_to_dataframe(inventory_levels):
    data = []
    for level in inventory_levels:
        # Convert the InventoryLevel object to a dictionary
        level_dict = level.attributes

        # Add location and inventory item details
        try:
            location = shopify.Location.find(level.location_id)
            level_dict['location_name'] = location.name
            level_dict['location_address1'] = location.address1
            level_dict['location_city'] = location.city
            level_dict['location_country'] = location.country
        except Exception as e:
            print(f"Error fetching location details: {e}")

        try:
            inventory_item = shopify.InventoryItem.find(level.inventory_item_id)
            level_dict['sku'] = inventory_item.sku
            level_dict['cost'] = inventory_item.cost
            level_dict['country_code_of_origin'] = inventory_item.country_code_of_origin
            level_dict['province_code_of_origin'] = inventory_item.province_code_of_origin
            level_dict['harmonized_system_code'] = inventory_item.harmonized_system_code
            level_dict['tracked'] = inventory_item.tracked
        except Exception as e:
            print(f"Error fetching inventory item details: {e}")

        data.append(level_dict)

    return pd.DataFrame(data)

def get_inventory_levels():
    all_inventory_levels = []
    locations = shopify.Location.find()
    products = get_all_resources(shopify.Product)

    for product in products:
        for variant in product.variants:
            for location in locations:
                time.sleep(1)  # at least 0.5
                inventory_level = shopify.InventoryLevel.find(inventory_item_ids=variant.inventory_item_id,
                                                              location_ids=location.id)
                if inventory_level:
                    all_inventory_levels.extend(inventory_level)
                    # Add product and variant information
                    for level in inventory_level:
                        level.attributes['product_id'] = product.id
                        level.attributes['product_title'] = product.title
                        level.attributes['variant_id'] = variant.id
                        level.attributes['variant_title'] = variant.title
                        level.attributes['variant_sku'] = variant.sku
                        level.attributes['variant_price'] = variant.price

    print(f"Total inventory levels retrieved: {len(all_inventory_levels)}")
    return all_inventory_levels
############################# INVENTORY #############################


############################# FULFILLMENT #############################
def get_fulfillments(order_id):
    order = shopify.Order.find(order_id)
    return order.fulfillments()


def fulfillments_to_dataframe(fulfillments):
    data = []
    for fulfillment in fulfillments:
        data.append({
            'id': fulfillment.id,
            'order_id': fulfillment.order_id,
            'status': fulfillment.status,
            'created_at': fulfillment.created_at,
            'updated_at': fulfillment.updated_at,
            'tracking_company': fulfillment.tracking_company,
            'tracking_number': fulfillment.tracking_number,
        })
    return pd.DataFrame(data)
############################# FULFILLMENT #############################


############################# ABANDONED CHECKOUTS #############################
def get_abandoned_checkouts():
    return get_all_resources(shopify.Checkout, status='any')


def abandoned_checkouts_to_dataframe(checkouts):
    data = []
    for checkout in checkouts:
        data.append({
            'id': checkout.id,
            'token': checkout.token,
            'cart_token': checkout.cart_token,
            'email': checkout.email,
            'created_at': checkout.created_at,
            'updated_at': checkout.updated_at,
            'completed_at': checkout.completed_at,
            'total_price': checkout.total_price,
        })
    return pd.DataFrame(data)
############################# ABANDONED CHECKOUTS #############################


############################# DISCOUNTS #############################
def get_price_rules():
    return get_all_resources(shopify.PriceRule)


def price_rules_to_dataframe(price_rules):
    data = []
    for rule in price_rules:
        data.append({
            'id': rule.id,
            'title': rule.title,
            'target_type': rule.target_type,
            'target_selection': rule.target_selection,
            'allocation_method': rule.allocation_method,
            'value_type': rule.value_type,
            'value': rule.value,
            'starts_at': rule.starts_at,
            'ends_at': rule.ends_at,
        })
    return pd.DataFrame(data)
############################# DISCOUNTS #############################


############################# REFUND #############################
def get_refunds(order_id):
    order = shopify.Order.find(order_id)
    return order.refunds()


def refunds_to_dataframe(refunds):
    data = []
    for refund in refunds:
        data.append({
            'id': refund.id,
            'order_id': refund.order_id,
            'created_at': refund.created_at,
            'note': refund.note,
            'restock': refund.restock,
        })
    return pd.DataFrame(data)
############################# REFUND #############################


############################# STORE INFORMATION #############################
def get_shop_info():
    return shopify.Shop.current()


def shop_info_to_dataframe(shop):
    data = [{
        'name': shop.name,
        'email': shop.email,
        'domain': shop.domain,
        'province': shop.province,
        'country': shop.country,
        'address1': shop.address1,
        'zip': shop.zip,
        'city': shop.city,
        'source': shop.source,
        'phone': shop.phone,
        'created_at': shop.created_at,
        'updated_at': shop.updated_at,
    }]
    return pd.DataFrame(data)
############################# STORE INFORMATION #############################


if __name__ == '__main__':
    initialize_session()

    # Get and save orders
    orders = get_orders()
    orders_df = orders_to_dataframe(orders)
    orders_df.to_csv('orders.csv', index=False)

    # Get and save products
    products = get_products()
    products_df = products_to_dataframe(products)
    products_df.to_csv('products.csv', index=False)

    # Get and save collections
    collections = get_collections()
    collections_df = collections_to_dataframe(collections)
    collections_df.to_csv('collections.csv', index=False)

    # ##################################################################
    # # Get and save inventory levels
    # inventory_levels = get_inventory_levels()
    # inventory_df = inventory_levels_to_dataframe(inventory_levels)
    # inventory_df.to_csv('inventory_levels.csv', index=False)
    # ##################################################################

    # # get and save fulfillment
    # order_id = orders_df['order_id'].iloc[0]
    # fulfillment = get_fulfillments(order_id)
    # fulfillment_df = collections_to_dataframe(fulfillment)
    # fulfillment_df.to_csv('fulfillment.csv', index=False)
    #
    # # get and save abandoned checkouts
    # abandoned_checkouts = get_abandoned_checkouts()
    # abandoned_checkouts_df = collections_to_dataframe(abandoned_checkouts)
    # abandoned_checkouts_df.to_csv('abandoned_checkouts.csv', index=False)

    # get and save discounts
    # discounts = get_
    # discounts_df = collections_to_dataframe(discounts)
    # discounts_df.to_csv('discounts.csv', index=False)

    # # get and save refund
    # refund = get_refunds()
    # refund_df = collections_to_dataframe(refund)
    # refund_df.to_csv('refund.csv', index=False)
    #
    # # get and save store information
    # store_info = get_shop_info()
    # store_info_df = collections_to_dataframe(store_info)
    # store_info_df.to_csv('store_information.csv', index=False)

    print("Data export complete.")

































