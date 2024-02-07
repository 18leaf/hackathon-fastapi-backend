from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from models.user_model import UserForm, UserAuth
from crud import user_crud as crud_user
from services.authentication import get_password_hash, get_current_active_user

router = APIRouter()


@router.post("/user/create_user")
async def create_user(user: UserForm):
    # validate if username or email taken, if not create account, initialize preferences to null
    if user.email:
        email_user = await crud_user.get_user_by_email(user.email)
        if email_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email Already Used"
            )

    username_user = await crud_user.get_user_by_username(user.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username Already Taken"
        )

    user.hashed_password = get_password_hash(user.hashed_password)

    result = await crud_user.create_user(user_data=user)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User could not be created"
        )

    return {"status": "Account Created Succesfully"}


@router.get("/user/me")
async def read_user_info(current_user: Annotated[UserAuth, Depends(get_current_active_user)]):
    users_info = await crud_user.get_user_by_username(current_user.username)
    return users_info