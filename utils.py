"""
Utility functions for the API
"""
import re
from database import get_db
from config import INSURANCE_RATE, MINIMUM_INSURANCE_FEE

def is_valid_email(email: str) -> bool:
    """
    Validate email format to prevent injection attacks.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 simplified email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


async def email_exists_in_db(email: str) -> bool:
    """
    Check if email exists in users collection.
    
    Args:
        email: Email string to check
        
    Returns:
        True if email exists, False otherwise
    """
    if not email:
        return False
    
    try:
        db = get_db()
        users = db["users"]
        user = await users.find_one({"email": email.lower()})
        return user is not None
    except Exception:
        return False


def format_price(price: float) -> str:
    """
    Format price with comma separators and 2 decimal places.
    
    Args:
        price: Numeric price value
        
    Returns:
        Formatted price string like "1,234.56"
    """
    return f"{price:,.2f}"


def format_rates_response(rates_list: list) -> list:
    """
    Format prices in rates list for display.
    
    Args:
        rates_list: List of rate dicts with 'weight' and 'price'
        
    Returns:
        List with prices formatted as strings
    """
    return [
        {
            "weight": rate["weight"],
            "price": format_price(rate["price"]),
            "price_raw": rate["price"]  # Keep raw for calculations if needed
        }
        for rate in rates_list
    ]


def calculate_insurance_fee(shipment_value: float) -> float:
    """
    Calculate insurance fee based on shipment value using tiered brackets.
    
    Args:
        shipment_value: The declared value of the shipment in NGN
        
    Returns:
        Calculated insurance fee based on value brackets
        
    Brackets:
        0 to 100,000: ₦5,000
        101,000 to 200,000: ₦7,500
        200,001 to 500,000: ₦10,000
        500,001 to 1,000,000: ₦20,000
        1,000,001 to 2,000,000: ₦30,000
        2,000,001 to 5,000,000: ₦120,000
        5,000,001 to 10,000,000: ₦240,000
        Above 10,000,000: ₦240,000 (max)
    """
    if not shipment_value or shipment_value <= 0:
        return 5000  # Default to lowest tier
    
    # Tiered insurance brackets
    if shipment_value <= 100000:
        return 5000
    elif shipment_value <= 200000:
        return 7500
    elif shipment_value <= 500000:
        return 10000
    elif shipment_value <= 1000000:
        return 20000
    elif shipment_value <= 2000000:
        return 30000
    elif shipment_value <= 5000000:
        return 120000
    elif shipment_value <= 10000000:
        return 240000
    else:
        # For values above 10,000,000, cap at highest tier
        return 240000


