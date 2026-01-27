from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from models import ShippingRate, ShippingRateResponse, PriceResponse
from database import get_db
from utils import format_price, format_rates_response
from auth import verify_api_key

router = APIRouter(prefix="/api", tags=["Shipping Rates"])

@router.get("/rates", response_model=List[ShippingRateResponse])
async def get_rates(zone: Optional[str] = None, api_key: str = Depends(verify_api_key)):
    """
    Get all shipping rates, optionally filtered by zone.
    
    Query parameters:
    - zone (optional): Filter by specific zone (e.g., UK_IRELAND)
    
    Returns prices formatted with commas (e.g., 1,234.56)
    """
    try:
        db = get_db()
        query = {}
        if zone:
            query["zone"] = zone.upper()
        
        collection = db["shipping_rates"]
        rates = await collection.find(query).to_list(length=None)
        
        if not rates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No shipping rates found"
            )
        
        # Format all prices with commas and convert ObjectId to string
        for rate in rates:
            rate["_id"] = str(rate["_id"])  # Convert ObjectId to string
            rate["rates"] = [
                {
                    "weight": r["weight"],
                    "price": format_price(r["price"])
                }
                for r in rate.get("rates", [])
            ]
        
        return rates
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rates: {str(e)}"
        )

@router.post("/add-rates", response_model=ShippingRateResponse, status_code=status.HTTP_201_CREATED)
async def add_rates(rate: ShippingRate, api_key: str = Depends(verify_api_key)):
    """
    Add a new shipping rate card or update an existing one.
    
    Request body example:
    ```json
    {
        "zone": "UK_IRELAND",
        "currency": "NGN",
        "unit": "kg",
        "rates": [
            {"weight": 2, "price": 85378.48},
            {"weight": 3, "price": 102410.07},
            {"weight": 4, "price": 126375.73}
        ]
    }
    ```
    """
    try:
        db = get_db()
        collection = db["shipping_rates"]
        
        # Ensure zone is uppercase
        rate.zone = rate.zone.upper()
        
        # Check if zone already exists
        existing = await collection.find_one({"zone": rate.zone})
        
        rate_dict = rate.model_dump()
        
        if existing:
            # Update existing zone
            result = await collection.update_one(
                {"zone": rate.zone},
                {"$set": rate_dict}
            )
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update rates"
                )
            # Return updated document
            updated = await collection.find_one({"zone": rate.zone})
            # Convert ObjectId to string and format prices
            updated["_id"] = str(updated["_id"])
            updated["rates"] = [
                {
                    "weight": r["weight"],
                    "price": format_price(r["price"])
                }
                for r in updated.get("rates", [])
            ]
            return updated
        else:
            # Insert new zone
            result = await collection.insert_one(rate_dict)
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to insert rates"
                )
            # Return inserted document
            inserted = await collection.find_one({"_id": result.inserted_id})
            # Convert ObjectId to string and format prices
            inserted["_id"] = str(inserted["_id"])
            inserted["rates"] = [
                {
                    "weight": r["weight"],
                    "price": format_price(r["price"])
                }
                for r in inserted.get("rates", [])
            ]
            return inserted
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding rates: {str(e)}"
        )

@router.get("/rates/{zone}/price", response_model=PriceResponse)
async def get_price(zone: str, weight: int, api_key: str = Depends(verify_api_key)):
    """
    Look up the price for a specific weight in a zone.
    
    Path parameters:
    - zone: Destination zone (e.g., UK_IRELAND)
    
    Query parameters:
    - weight: Weight in kg
    """
    try:
        db = get_db()
        collection = db["shipping_rates"]
        
        rate_doc = await collection.find_one({
            "zone": zone.upper(),
            "rates.weight": weight
        }, {"rates.$": 1})
        
        if not rate_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No rate found for {weight}kg to {zone}"
            )
        
        price_entry = rate_doc["rates"][0]
        return {
            "zone": zone.upper(),
            "weight": price_entry["weight"],
            "price": format_price(price_entry["price"]),
            "currency": rate_doc.get("currency", "NGN")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching price: {str(e)}"
        )
