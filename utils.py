"""
Utility functions for the API
"""
import re
from database import get_db

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

