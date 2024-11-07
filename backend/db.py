from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import Models.schema as schema

# MongoDB client setup
client = AsyncIOMotorClient("mongodb://localhost:27017")  # MongoDB URI
db = client["bicycle_store"]  # Database name

# Get collections
products_collection = db["products"]
parts_collection = db["parts"]
variations_collection = db["variations"]
flows_collection = db["flows"]
reviews_collection = db["reviews"]
orders_collection = db["orders"]
transactions_collection = db["transactions"]
support_cases_collection = db["support_cases"]
logs_collection = db["logs"]

# Insert a product
async def create_product(name, description, images, parts, available_stock):
    # create product object
    product = schema.Product(
        name=name,
        description=description,
        images=images,
        parts=parts,
        available_stock=available_stock
    )
    
    # insert product object into db
    result = await products_collection.insert_one(product.dict())

    # log
    print(f"Inserted product with id: {result.inserted_id}")

# Insert a part
async def create_part(product_id, name, icon, variations):
    # create part object
    part = schema.Part(
        product_id=schema.ObjectId("672d33d89673b3ada5048ffe"),
        name="Wheels",
        icon="https://s3.amazonaws.com/bucket-name/product1-image1.jpg",
        variations=[schema.ObjectId(), schema.ObjectId()],
    )
    
    # insert part object into db
    result = await parts_collection.insert_one(part.dict())

    # log
    print(f"Inserted part with id: {result.inserted_id}")

# TODO: Insert a variation
async def create_variation():
    pass

# TODO: Get all products
async def get_all_products():
    pass

# TODO: Get a product by name
async def get_product_by_name():
    pass

# TODO: Get a product by ID
async def get_product_by_id():
    pass

# TODO: Get all parts
async def get_all_parts(product_id):
    pass

# TODO: Get all variations
async def get_all_variations(part_id):
    pass

