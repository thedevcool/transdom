from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union
from bson import ObjectId

class RateEntry(BaseModel):
    """Individual weight-price pair"""
    weight: int = Field(..., description="Weight in kg (e.g., 2, 3, 4)")
    price: Union[float, str] = Field(..., description="Price in NGN (numeric or formatted string)")

class ShippingRate(BaseModel):
    """Shipping rate for a zone"""
    zone: str = Field(..., description="Destination zone (e.g., UK_IRELAND, USA_CANADA)")
    currency: str = Field(default="NGN", description="Currency code")
    unit: str = Field(default="kg", description="Weight unit")
    rates: List[RateEntry] = Field(..., description="List of weight-price pairs")

class ShippingRateResponse(ShippingRate):
    """Response model with MongoDB _id"""
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class PriceResponse(BaseModel):
    """Price lookup response"""
    zone: str
    weight: int
    price: str  # Formatted price string like "1,234.56"
    currency: str
