from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves the profile information of the currently authenticated user.

    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: The profile information of the current user.
    :rtype: UserDb
    :raises HTTPException: If there is an error retrieving the user's profile data.
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Updates the avatar's profile picture of the currently authenticated user.
    The avatar image will be uploaded to Cloudinary, resized, and the public URL will be saved to the user's profile.

    :param file: The avatar image file to upload.
    :type file: UploadFile
    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The updated user information including the new avatar URL.
    :rtype: UserDb
    :raises HTTPException: If there is an error during the avatar upload process or user update.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
