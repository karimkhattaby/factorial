import asyncio
import db

# initiate db
def create_products():
    name="Bicycle"
    description="Customizable bicycle"
    images=["https://s3.amazonaws.com/bucket-name/product1-image1.jpg", 
            "https://s3.amazonaws.com/bucket-name/product1-image2.jpg"]
    parts=[]
    available_stock=1

    asyncio.run(db.create_product(name, description, images, parts, available_stock))

async def create_parts():
    product_id="672d3a864271def20e147ab8"
    
    for name in ['Wheels', 'Frame Type', 'Frame Finish', 'Rim Color', 'Chain']:
        icon="https://s3.amazonaws.com/bucket-name/product1-image1.jpg"
        variations=[]
        await db.create_part(product_id, name, icon, variations)

asyncio.run(create_parts())