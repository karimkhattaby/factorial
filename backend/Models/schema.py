from typing import List, Optional
from pydantic import BaseModel, Field
from bson.objectid import ObjectId as BsonObjectId
import datetime

class ObjectId(BsonObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, BsonObjectId):
            raise TypeError('ObjectId required')
        return str(v)

class Product(BaseModel):
    """
        Stores information about products and associated customization parts
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id") # MongoDB automatically generates this
    name: str
    description: str
    images: List[str]  # List of image URLs (S3 bucket links)
    parts: List[ObjectId]  # List of part IDs associated with this product
    available_stock: int

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types like ObjectId
        json_encoders = {ObjectId: str}  # Convert ObjectId to string when serializing

class Part(BaseModel):
    """
        Stores information about customization parts and the associated variations
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    product_id: ObjectId  # Reference to the parent product
    name: str
    icon: str  # Icon image URL
    variations: List[ObjectId]  # List of variation IDs

    class Config:
        json_encoders = {ObjectId: str}

class Variation(BaseModel):
    """
        Contains variants of parts, prohibited dependencies, and dependency-based pricing
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    part_id: ObjectId  # Reference to the parent part
    name: str
    images: List[str]  # List of image URLs for this variation
    prohibited_dependencies: List[ObjectId]  # List of variation IDs this variation CANNOT be combined with
    prices: List[dict]  # List of prices, each with a possible dependency part
    available_stock: int

    class Config:
        json_encoders = {ObjectId: str}

class Flow(BaseModel):
    """
        Stores the customer's journey (order in which parts will show to the user)
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    product_id: ObjectId  # Reference to the product
    parts: List[ObjectId]  # List of parts that are customizable for this product

    class Config:
        json_encoders = {ObjectId: str}

class Review(BaseModel):
    """
        Stores customer's reviews
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    product_id: ObjectId  # Reference to the product
    order_id: ObjectId  # Reference to the order associated with the review, used to verify the purchase
    rating: float
    title: str
    description: str
    author: ObjectId  # Reference to the user who wrote the review
    created_at: datetime.datetime
    helpful_count: int = 0  # Number of times other users liked the review
    report_count: int = 0  # Number of times other users reported the review

    class Config:
        json_encoders = {ObjectId: str}

class SelectedVariation(BaseModel):
    """
        Object that has the ID and price of the selected variation
    """
    selected_variation: ObjectId # Reference to the variation
    price: float # Variation purchase price

class OrderItem(BaseModel):
    """
        Object that stores selected product, variations, and purchase prices
    """
    product_id: ObjectId  # Reference to the product
    selected_variations: List[SelectedVariation]  # List of selected variation IDs and prices

class Order(BaseModel):
    """
        List of orders placed by customers, price, and status
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    user_id: ObjectId  # Reference to the user who placed the order
    items: List[OrderItem]  # List of order items
    status: str  # Status of the order (e.g., "pending", "shipped")
    total_price: float  # Total price of the order
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        json_encoders = {ObjectId: str}

class Transaction(BaseModel):
    """
        List of transactions performed by users
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    order_id: ObjectId  # Reference to the order this transaction is associated with
    payment_method: str  # Payment method (e.g., "stripe", "paypal", "cash")
    payment_status: str  # Status of the payment (e.g., "completed", "pending", "failed")
    transaction_id: str  # Unique transaction ID provided by the payment gateway
    transaction_date: datetime.datetime  # Date of the transaction as provided by the payment gateway
    amount: float  # Amount of the transaction
    currency: str  # Currency (e.g., "USD", "EUR")
    payment_details: dict  # Details of the payment method (e.g., last4 digits of card & card type, or paypal_email. Details might be specific to each payment gateway)
    payment_gateway: str  # Payment gateway used (e.g., "stripe", "paypal")
    created_at: datetime.datetime # Timestamp when the transaction was created
    updated_at: datetime.datetime # Timestamp when the transaction was last updated

    class Config:
        json_encoders = {ObjectId: str}

class SupportCase(BaseModel):
    """
        Tracks customer support cases and stores exchanged messages

        Format of messages:
        'Customer: '
        'Support: '
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    subject: str 
    category: str  # Category of the issue (e.g., "Technical", "Order Issues")
    owner_id: ObjectId  # Reference to the support agent handling the case
    customer_id: ObjectId  # Reference to the customer who submitted the case
    status: str  # Case status (e.g., "open", "closed", "in-progress")
    messages: List[str]  # List of messages exchanged
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        json_encoders = {ObjectId: str}

class Log(BaseModel):
    """
        Stores logs of users actions
    """
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    user_id: ObjectId  # Reference to the user who performed the action
    action: str  # Action performed (e.g., "viewed product")
    timestamp: datetime.datetime

    class Config:
        json_encoders = {ObjectId: str}
