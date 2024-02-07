from typing import Annotated

from crud.user_crud import get_user_by_username, get_user
from datetime import datetime, timedelta
from core.config import settings
from models.user_model import UserAuth, UserAuthPass

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel

from jose import JWTError, jwt
from passlib.context import CryptContext

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(username: str, password: str) -> UserAuthPass | bool:
    user = await get_user_by_username(username=username)
    # if user in DB password does not align after beingh hashed re
    if not verify_password(password=password, hashed=user.hashed_password):
        # return false could not authenticate
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # unpack id from token data, check db for user, return user model
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could Not Validate Credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credential_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credential_exception
    user = await get_user(user_id=token_data.user_id)
    if not user:
        raise credential_exception
    return user


async def get_current_active_user(current_user: Annotated[UserAuth, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(
            status_code=400,
            detail="Inactive User Token"
        )
    return current_user


async def is_admin(current_user: Annotated[UserAuth, Depends(get_current_active_user)]) -> bool:
    if current_user.is_admin:
        return True
    return False


router = APIRouter()


# create access token for session = 30 minutes
@router.post("/auth/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    ''' INFO ON /api/token Fetch Params

     OAuth2PAsswordRequestForm Data = {
    grant_type: 'password',
    username: 'your_username',
    password: 'your_password',
    scope: ''
    };

    Content-Type: 'application/x-www-form-urlencoded',
    '''
    user = await authenticate_user(username=form_data.username,
                                   password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
