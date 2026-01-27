"""
Utility functions for the API
"""

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
