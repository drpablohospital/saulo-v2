"""Auth dependencies for Saulo v2."""
from fastapi import Depends
from auth.router import get_current_user_optional


async def get_current_user_optional_dep(user=Depends(get_current_user_optional)):
    """Dependency to get optional current user."""
    return user