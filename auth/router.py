"""Auth router for Saulo v2."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt

from auth.utils import verify_password, ADMIN_USERNAME, ADMIN_PASSWORD_HASH

router = APIRouter(prefix="/auth", tags=["auth"])

# JWT settings
SECRET_KEY = "saulo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    username: str
    is_admin: bool


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user_optional(token: str = Depends(oauth2_scheme)):
    """Get current user from token (optional)."""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return {"user_id": username, "is_admin": True}
    except JWTError:
        return None


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint."""
    # Check credentials
    if request.username != ADMIN_USERNAME:
        raise HTTPException(
            status_code=401,
            detail="Usuario incorrecto"
        )
    
    if not verify_password(request.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(
            status_code=401,
            detail="Contraseña incorrecta"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user_optional)):
    """Get current user info."""
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    return {"username": user["user_id"], "is_admin": True}


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)."""
    return {"message": "Logout successful"}