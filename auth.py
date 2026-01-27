from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import os

VALID_API_KEY = os.getenv("API_KEY", "transdom-api-key")

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from X-API-Key header"""
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key required in X-API-Key header"
        )
    
    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return x_api_key
