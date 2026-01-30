from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from models import (
    ShippingRate,
    ShippingRateResponse,
    PriceResponse,
    UserSignup,
    UserLogin,
    TokenResponse,
    SignupResponse,
    UserPublic,
    AdminSignup,
    AdminLogin,
    AdminTokenResponse,
    AdminPublic,
    PaymentRequest,
    Payment,
    MakeOrderRequest,
    Order,
    ApproveOrderRequest,
    ValidateRequest,
    AdminShipmentsResponse,
)
from database import get_db
from utils import format_price, format_rates_response, is_valid_email, email_exists_in_db
from auth import (
    verify_api_key,
    get_password_hash,
    authenticate_user,
    create_access_token,
    authenticate_admin,
    get_current_admin,
    get_current_user,
)
from datetime import datetime
from bson import ObjectId
from typing import Optional

router = APIRouter(prefix="/api", tags=["Shipping Rates"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserSignup):
    """Register a new user, return an access token and public user info"""
    try:
        db = get_db()
        users = db["users"]
        email = payload.email.lower()
        existing = await users.find_one({"email": email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        user_dict = payload.model_dump()
        user_dict["email"] = email
        # Handle bcrypt 72-byte limit: truncate password bytes to 72 bytes
        raw_password = user_dict.pop("password")
        if isinstance(raw_password, str):
            raw_bytes = raw_password.encode("utf-8")
        else:
            raw_bytes = bytes(raw_password)
        if len(raw_bytes) > 72:
            # Truncate bytes and decode safely (ignore partial char at end)
            raw_bytes = raw_bytes[:72]
            raw_password = raw_bytes.decode("utf-8", errors="ignore")
        user_dict["hashed_password"] = get_password_hash(raw_password)
        user_dict["created_at"] = datetime.utcnow()

        result = await users.insert_one(user_dict)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

        access_token = create_access_token({"sub": email})

        # Build public user payload for frontend embedding
        user_public = {
            "firstname": payload.firstname,
            "lastname": payload.lastname,
            "gender": payload.gender,
            "email": email,
            "phone_number": payload.phone_number,
            "country": payload.country,
            "referral_code": payload.referral_code,
            "photo_url": payload.photo_url,
        }

        return {"access_token": access_token, "token_type": "bearer", "user": user_public}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    """Authenticate user and return JWT access token"""
    try:
        user = await authenticate_user(payload.email, payload.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        access_token = create_access_token({"sub": user.get("email")})
        # Build public user payload for frontend embedding
        user_public = {
            "firstname": user.get("firstname"),
            "lastname": user.get("lastname"),
            "gender": user.get("gender"),
            "email": user.get("email"),
            "phone_number": user.get("phone_number"),
            "country": user.get("country"),
            "referral_code": user.get("referral_code"),
            "photo_url": user.get("photo_url"),
        }

        return {"access_token": access_token, "token_type": "bearer", "user": user_public}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )


@router.get("/rates", response_model=List[ShippingRateResponse])
async def get_rates(zone: Optional[str] = None):
    """
    Get all shipping rates, optionally filtered by zone (public - no auth required).

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
async def add_rates(rate: ShippingRate, admin: dict = Depends(get_current_admin)):
    """
    Add a new shipping rate card or update an existing one (admin only).

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
            detail=f"Error adding/updating rates: {str(e)}"
        )


@router.get("/rates/{zone}/price", response_model=PriceResponse)
async def get_price_for_zone_weight(zone: str, weight: float):
    """
    Get price for a specific zone and weight (public - no auth required).
    Finds the smallest weight tier that can accommodate the given weight.

    Path parameters:
    - zone: Zone code (e.g., UK_IRELAND)

    Query parameters:
    - weight: Weight in kg

    Returns the price for the matched weight tier with commas (e.g., 1,234.56)
    """
    try:
        if weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Weight must be greater than 0"
            )

        db = get_db()
        collection = db["shipping_rates"]
        zone_upper = zone.upper()

        # Find the zone document
        zone_doc = await collection.find_one({"zone": zone_upper})

        if not zone_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zone '{zone}' not found"
            )

        rates = zone_doc.get("rates", [])
        if not rates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No rates defined for zone '{zone}'"
            )

        # Sort rates by weight
        sorted_rates = sorted(rates, key=lambda x: x["weight"])

        # Find the smallest weight tier >= requested weight
        matched_rate = None
        for rate in sorted_rates:
            if rate["weight"] >= weight:
                matched_rate = rate
                break

        # If no exact match or larger tier, use the largest available
        if matched_rate is None:
            matched_rate = sorted_rates[-1]

        return {
            "zone": zone_upper,
            "weight": matched_rate["weight"],
            "price": format_price(matched_rate["price"]),
            "currency": zone_doc.get("currency", "NGN")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching price: {str(e)}"
        )


@router.get("/zones", response_model=List[str])
async def get_zones():
    """
    Get list of all available shipping zones in the database.
    
    Returns a sorted list of zone codes (e.g., ['ASIA', 'EUROPE', 'UK_IRELAND', ...])
    """
    try:
        db = get_db()
        collection = db["shipping_rates"]
        
        # Get distinct zone values
        zones = await collection.distinct("zone")
        
        if not zones:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No zones found in database"
            )
        
        return sorted(zones)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching zones: {str(e)}"
        )


# ============ ADMIN ENDPOINTS ============

@router.post("/admin/signup", response_model=AdminTokenResponse, status_code=status.HTTP_201_CREATED)
async def admin_signup(payload: AdminSignup):
    """Register a new admin, return an access token"""
    try:
        db = get_db()
        admins = db["admins"]

        # Check if admin with this name already exists
        existing = await admins.find_one({"name": payload.name})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin with this name already exists"
            )

        admin_dict = payload.model_dump()
        # Handle bcrypt 72-byte limit
        raw_password = admin_dict.pop("password")
        if isinstance(raw_password, str):
            raw_bytes = raw_password.encode("utf-8")
        else:
            raw_bytes = bytes(raw_password)
        if len(raw_bytes) > 72:
            raw_bytes = raw_bytes[:72]
            raw_password = raw_bytes.decode("utf-8", errors="ignore")
        admin_dict["hashed_password"] = get_password_hash(raw_password)
        admin_dict["created_at"] = datetime.utcnow()

        result = await admins.insert_one(admin_dict)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create admin"
            )

        access_token = create_access_token({"sub": payload.name})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin": {"name": payload.name, "role": "admin"}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating admin: {str(e)}"
        )


@router.post("/admin/login", response_model=AdminTokenResponse)
async def admin_login(payload: AdminLogin):
    """Authenticate admin and return JWT access token"""
    try:
        admin = await authenticate_admin(payload.name, payload.password)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect name or password"
            )
        access_token = create_access_token({"sub": admin.get("name")})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin": {"name": admin.get("name"), "role": "admin"}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during admin login: {str(e)}"
        )


@router.post("/validate", status_code=status.HTTP_200_OK)
async def validate_api_key(payload: ValidateRequest, api_key: str = Depends(verify_api_key)):
    """
    Validate API key endpoint - protected by API key header.
    Returns 200 OK if API key is valid, 401/403 otherwise.
    """
    return {"message": "API key is valid", "validated": True}


# ============ PAYMENT ENDPOINTS ============

@router.post("/log-payment", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def log_payment(payload: PaymentRequest, user: dict = Depends(get_current_user)):
    """Log a successful payment (user only)"""
    try:
        db = get_db()
        payments = db["payments"]

        payment_dict = payload.model_dump()
        payment_dict["user_email"] = user.get("email")
        payment_dict["created_at"] = datetime.utcnow()

        result = await payments.insert_one(payment_dict)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log payment"
            )

        # Return the created payment
        payment = await payments.find_one({"_id": result.inserted_id})
        payment["_id"] = str(payment.get("_id"))
        return payment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging payment: {str(e)}"
        )


# ============ ORDER ENDPOINTS ============

@router.post("/make-order", response_model=Order, status_code=status.HTTP_201_CREATED)
async def make_order(payload: MakeOrderRequest, user: dict = Depends(get_current_user)):
    """
    Create a new order with complete booking details (user only)

    Request body must include all sender, receiver, and shipment details as flat fields
    """
    try:
        # Validate sender email format
        if not is_valid_email(payload.sender_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sender email format"
            )

        # Check if email exists in users collection
        email_exists = await email_exists_in_db(payload.sender_email)
        if not email_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender email not registered in our database"
            )

        db = get_db()
        orders = db["orders"]

        # Get the next order number
        counter = db["counters"]
        count_doc = await counter.find_one_and_update(
            {"_id": "order_count"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        order_num = count_doc.get("seq", 1)

        # Generate order_no: transdom_order{num}_{date}
        date_str = datetime.utcnow().strftime("%Y%m%d")
        order_no = f"transdom_order{order_num}_{date_str}"

        order_dict = {
            "order_no": order_no,
            "zone_picked": payload.zone_picked.upper(),
            "delivery_speed": payload.delivery_speed,
            "amount_paid": payload.amount_paid,
            "status": "pending",
            "date_created": datetime.utcnow(),
            # Sender details
            "sender_name": payload.sender_name,
            "sender_phone": payload.sender_phone,
            "sender_address": payload.sender_address,
            "sender_state": payload.sender_state,
            "sender_city": payload.sender_city,
            "sender_country": payload.sender_country,
            "sender_email": payload.sender_email.lower(),
            # Receiver details
            "receiver_name": payload.receiver_name,
            "receiver_phone": payload.receiver_phone,
            "receiver_address": payload.receiver_address,
            "receiver_state": payload.receiver_state,
            "receiver_city": payload.receiver_city,
            "receiver_post_code": payload.receiver_post_code,
            "receiver_country": payload.receiver_country,
            # Shipment details
            "shipment_description": payload.shipment_description,
            "shipment_quantity": payload.shipment_quantity,
            "shipment_value": payload.shipment_value,
            "shipment_weight": payload.shipment_weight,
        }

        result = await orders.insert_one(order_dict)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create order"
            )

        # Return the created order
        order = await orders.find_one({"_id": result.inserted_id})
        order["_id"] = str(order.get("_id"))
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )

@router.post("/log-order-activity", status_code=status.HTTP_201_CREATED)
async def log_order_activity(
        order_no: str,
        activity_type: str,
        description: Optional[str] = None,
        user: dict = Depends(get_current_user)
):
    """
    Log activity for an order (user only).

    Activity types:
    - created: Order was created
    - paid: Payment confirmed
    - viewed: Order viewed in dashboard
    - status_changed: Status was updated
    """
    try:
        db = get_db()
        order_logs = db["order_logs"]

        log_entry = {
            "order_no": order_no,
            "activity_type": activity_type,
            "description": description,
            "user_email": user.get("email"),
            "timestamp": datetime.utcnow(),
            "ip_address": None,  # Could be extracted from request if needed
        }

        result = await order_logs.insert_one(log_entry)

        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log order activity"
            )

        return {
            "message": "Activity logged successfully",
            "log_id": str(result.inserted_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging order activity: {str(e)}"
        )


@router.get("/order-logs/{order_no}")
async def get_order_logs(
        order_no: str,
        user: dict = Depends(get_current_user)
):
    """
    Get activity logs for a specific order.
    Users can only view logs for their own orders.
    """
    try:
        db = get_db()
        orders = db["orders"]
        order_logs = db["order_logs"]

        # Verify the order belongs to this user
        user_email = user.get("email")
        order = await orders.find_one({
            "order_no": order_no,
            "email": user_email.lower()
        })

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or you don't have access to it"
            )

        # Get all logs for this order
        logs = await order_logs.find(
            {"order_no": order_no}
        ).sort("timestamp", -1).to_list(length=None)

        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log.get("_id"))

        return {
            "order_no": order_no,
            "logs": logs,
            "total": len(logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order logs: {str(e)}"
        )


@router.get("/admin/order-logs/{order_no}")
async def admin_get_order_logs(
        order_no: str,
        admin: dict = Depends(get_current_admin)
):
    """
    Get activity logs for a specific order (admin only).
    Admins can view logs for any order.
    """
    try:
        db = get_db()
        order_logs = db["order_logs"]

        # Get all logs for this order
        logs = await order_logs.find(
            {"order_no": order_no}
        ).sort("timestamp", -1).to_list(length=None)

        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log.get("_id"))

        return {
            "order_no": order_no,
            "logs": logs,
            "total": len(logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order logs: {str(e)}"
        )


@router.get("/shipments", response_model=List[Order])
async def get_user_shipments(user: dict = Depends(get_current_user)):
    """
    Get all shipments/orders for the authenticated user.
    Returns orders sorted by date (newest first) with complete booking details.
    """
    try:
        # Get the authenticated user's email
        user_email = user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User email not found in token"
            )

        db = get_db()
        orders = db["orders"]

        # Find all orders for this user's email (matching sender_email)
        user_orders = await orders.find(
            {"sender_email": user_email.lower()}
        ).sort("date_created", -1).to_list(length=None)

        # Convert ObjectId to string for all orders
        for order in user_orders:
            order["_id"] = str(order.get("_id"))

        # Return just the list, not wrapped in {"shipments": ...}
        return user_orders
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching shipments: {str(e)}"
        )


@router.get("/shipments/{order_no}", response_model=Order)
async def get_shipment_by_order_no(order_no: str, user: dict = Depends(get_current_user)):
    """
    Get a specific shipment by order number.
    Users can only access their own shipments.
    """
    try:
        user_email = user.get("email")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User email not found in token"
            )

        db = get_db()
        orders = db["orders"]

        # Find the order and verify it belongs to this user
        order = await orders.find_one({
            "order_no": order_no,
            "sender_email": user_email.lower()
        })

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_no} not found or you don't have access to it"
            )

        order["_id"] = str(order.get("_id"))
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching shipment: {str(e)}"
        )


@router.get("/admin/shipments", response_model=AdminShipmentsResponse)
async def get_all_shipments(
        admin: dict = Depends(get_current_admin),
        status_filter: Optional[str] = None,
        email: Optional[str] = None,
        limit: int = 100
):
    """
    Get all shipments (admin only) with complete booking details.
    Can filter by status or email.

    Query parameters:
    - status_filter: Filter by order status (pending, approved, rejected)
    - email: Filter by sender email
    - limit: Maximum number of results (default 100)
    """
    try:
        db = get_db()
        orders = db["orders"]

        # Build query
        query = {}
        if status_filter:
            query["status"] = status_filter.lower()
        if email:
            query["sender_email"] = email.lower()

        # Get orders sorted by date (newest first)
        all_orders = await orders.find(query).sort(
            "date_created", -1
        ).limit(limit).to_list(length=limit)

        # Convert ObjectId to string
        for order in all_orders:
            order["_id"] = str(order.get("_id"))

        return {"shipments": all_orders, "count": len(all_orders)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching shipments: {str(e)}"
        )


@router.post("/admin/approve-order", response_model=Order)
async def approve_order(payload: ApproveOrderRequest, admin: dict = Depends(get_current_admin)):
    """
    Approve or reject an order (admin only).

    Updates the status of an order to 'approved', 'rejected', or 'pending'.

    Request body:
    {
        "order_no": "transdom_order1_20260129",
        "status": "approved"  // or "rejected" or "pending"
    }
    """
    try:
        db = get_db()
        orders = db["orders"]

        # Validate status
        valid_statuses = ["pending", "approved", "rejected"]
        if payload.status.lower() not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        # Find and update the order
        updated = await orders.find_one_and_update(
            {"order_no": payload.order_no},
            {"$set": {"status": payload.status.lower()}},
            return_document=True
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {payload.order_no} not found"
            )

        updated["_id"] = str(updated.get("_id"))
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving order: {str(e)}"
        )

# ============ DELETE ORDER ENDPOINTS (ADMIN ONLY) ============

@router.delete("/admin/orders", status_code=status.HTTP_200_OK)
async def delete_all_orders(admin: dict = Depends(get_current_admin)):
    """
    Delete ALL orders from the database (admin only).
    Use with extreme caution - this action cannot be undone!

    Returns the count of deleted orders.
    """
    try:
        db = get_db()
        orders = db["orders"]

        # Count orders before deletion
        count = await orders.count_documents({})

        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No orders found to delete"
            )

        # Delete all orders
        result = await orders.delete_many({})

        return {
            "message": f"Successfully deleted {result.deleted_count} orders",
            "deleted_count": result.deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting orders: {str(e)}"
        )


@router.delete("/admin/orders/{order_id}", status_code=status.HTTP_200_OK)
async def delete_order_by_id(order_id: str, admin: dict = Depends(get_current_admin)):
    """
    Delete a specific order by its MongoDB _id (admin only).

    Path parameters:
    - order_id: The MongoDB ObjectId of the order (as a string)

    Returns confirmation of deletion.
    """
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(order_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid order ID format: {order_id}"
            )

        db = get_db()
        orders = db["orders"]

        # Find the order first to get details
        order = await orders.find_one({"_id": ObjectId(order_id)})

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )

        # Delete the order
        result = await orders.delete_one({"_id": ObjectId(order_id)})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete order"
            )

        return {
            "message": f"Successfully deleted order {order.get('order_no', 'unknown')}",
            "deleted_order_id": order_id,
            "order_no": order.get("order_no"),
            "email": order.get("email")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting order: {str(e)}"
        )