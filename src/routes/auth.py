from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Registers a new user and sends a confirmation email to the user's provided email address.
    The user's password is hashed before being stored in the database, and a background task is used
    to send a confirmation email with a verification token.

    :param body: The data required to create a new user.
    :type body: UserModel
    :param background_tasks: Background tasks for sending the confirmation email.
    :type background_tasks: BackgroundTasks
    :param request: Request object, used to get the base URL for generating the confirmation link.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: The created user and a message indicating the success of the operation.
    :rtype: dict
    :raises HTTPException: If the email is already registered (409 Conflict).
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and generates an access token and refresh token.

    :param body: The login credentials, including username (email) and password.
    :type body: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: Session
    :return: A dictionary containing the access token, refresh token, and token type (Bearer).
    :rtype: dict
    :raises HTTPException: If the email is invalid, the email is not confirmed, or the password is incorrect (401 Unauthorized).
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refreshes an access token using a valid refresh token.

    :param credentials: The credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: The database session.
    :type db: Session
    :return: A dictionary containing the new access token, refresh token, and token type (Bearer).
    :rtype: dict
    :raises HTTPException: If the refresh token is invalid or expired (401 Unauthorized).
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms the user's email address by verifying the provided token.

    :param token: The email confirmation token.
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: A message indicating the success or failure of the email confirmation process.
    :rtype: dict
    :raises HTTPException: If the verification token is invalid or the email does not exist (400 Bad Request).
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Requests a new email confirmation for an unconfirmed email address.

    :param body: The data containing the email address to request confirmation for.
    :type body: RequestEmail
    :param background_tasks: Background tasks for sending the confirmation email.
    :type background_tasks: BackgroundTasks
    :param request: Request object, used to get the base URL for generating the confirmation link.
    :type request: Request
    :param db: The database session.
    :type db: Session
    :return: A message indicating the success or failure of the email confirmation request.
    :rtype: dict
    :raises HTTPException: If the email is already confirmed.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
