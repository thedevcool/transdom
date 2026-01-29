# Replace the get_user_shipments function in your routes.py (line 527-561) with this:

@router.get("/shipments", response_model=List[Order])
async def get_user_shipments(user: dict = Depends(get_current_user)):
    """
    Get all shipments/orders for the authenticated user.
    Returns orders sorted by date (newest first).
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
        
        # Find all orders for this user's email
        user_orders = await orders.find(
            {"email": user_email.lower()}
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
