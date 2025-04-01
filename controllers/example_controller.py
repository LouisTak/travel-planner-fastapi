from fastapi import APIRouter, Depends
from middleware.jwt_auth import JWTBearer
from models.user_role import UserRole

router = APIRouter()

# Create different JWT bearer instances for different role requirements
auth_bearer = JWTBearer()  # Basic authentication
admin_bearer = JWTBearer(allowed_roles=[UserRole.ADMIN.value])  # Admin only
premium_bearer = JWTBearer(allowed_roles=[UserRole.PREMIUM.value, UserRole.ADMIN.value])  # Premium and admin

@router.get("/protected")
async def protected_route(credentials = Depends(auth_bearer)):
    print(credentials)
    """Example of a protected route that requires any valid JWT token."""
    return {"message": "This is a protected route"}

@router.get("/admin-only")
async def admin_route(credentials = Depends(admin_bearer)):
    """Example of a route that requires admin role."""
    return {"message": "This is an admin-only route"}

@router.get("/premium-feature")
async def premium_route(credentials = Depends(premium_bearer)):
    """Example of a route that requires premium role."""
    return {"message": "This is a premium feature"}