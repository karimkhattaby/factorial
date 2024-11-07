"""
Assumptions:
1- database is already initiated
2- all mongodb interface functions are implemented
"""

import db

# Customers interface

async def get_products():
    # retrieve products
    results = db.get_all_products()

    return results

async def get_parts(product_id):
    # retrieve parts
    results = db.get_all_parts(product_id)

    return results

async def get_variations(part_id):
    # retrieve variations
    results = db.get_all_variations(part_id)

    return results

async def toggle_stock(variation_id, toggle):
    result = db.toggle_stock(variation_id, toggle)
    
    return result

async def checkout(details):
    results = db.create_order(details)

    return result