from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


VALID_API_KEY = os.getenv("API_KEY", "transdom-api-key")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(email: str, password: str):
    db = get_db()
    users = db["users"]
    user = await users.find_one({"email": email.lower()})
    if not user:
        return None
    hashed = user.get("hashed_password")
    if not hashed or not verify_password(password, hashed):
        return None
    # return user dict
    user["_id"] = str(user.get("_id"))
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_db()["users"].find_one({"email": email.lower()})
    if user is None:
        raise credentials_exception
    user["_id"] = str(user.get("_id"))
    return user


# Admin authentication functions
async def authenticate_admin(name: str, password: str):
    db = get_db()
    admins = db["admins"]
    admin = await admins.find_one({"name": name})
    if not admin:
        return None
    hashed = admin.get("hashed_password")
    if not hashed or not verify_password(password, hashed):
        return None
    admin["_id"] = str(admin.get("_id"))
    return admin


async def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_name: str = payload.get("sub")
        if admin_name is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    admin = await get_db()["admins"].find_one({"name": admin_name})
    if admin is None:
        raise credentials_exception
    admin["_id"] = str(admin.get("_id"))
    return admin

