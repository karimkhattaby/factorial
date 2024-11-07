from typing import List, Optional
from pydantic import BaseModel, Field

class SelectedVariation(BaseModel):
    selected_variation: str # Reference to the variation
    price: float # Variation purchase price

class OrderItem(BaseModel):
    product_id: str  # Reference to the product
    selected_variations: List[SelectedVariation]  # List of selected variation IDs and prices

class OrderDetails(BaseModel):
    user_id: str  # Reference to the user who placed the order
    items: List[OrderItem]  # List of order items
    total_price: float  # Total price of the order

class TransactionDetails(BaseModel):
    payment_method: str  # Payment method (e.g., "stripe", "paypal", "cash")
    payment_status: str  # Status of the payment (e.g., "completed", "pending", "failed")
    transaction_id: str  # Unique transaction ID provided by the payment gateway
    transaction_date: str  # Date of the transaction as provided by the payment gateway
    amount: float  # Amount of the transaction
    currency: str  # Currency (e.g., "USD", "EUR")
    payment_details: dict  # Details of the payment method (e.g., last4 digits of card & card type, or paypal_email. Details might be specific to each payment gateway)
    payment_gateway: str  # Payment gateway used (e.g., "stripe", "paypal")