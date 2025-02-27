import redis
from typing import Optional
from jose import JWTError, jwt

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if the provided plain password matches the hashed password.

        :param plain_password: The plain text password provided by the user.
        :type plain_password: str
        :param hashed_password: The hashed password stored in the database.
        :type hashed_password: str
        :return: `True` if the passwords match, `False` otherwise.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hashes the provided plain text password.

        :param password: The plain text password to be hashed.
        :type password: str
        :return: The hashed version of the provided password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates an access token with the provided data and expiration time.

        :param data: A dictionary containing the payload to be included in the token.
        :type data: dict
        :param expires_delta: The expiration time in seconds for the access token. If not provided,
                               the token will expire in 15 minutes by default.
        :type expires_delta: Optional[float]
        :return: The encoded access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a refresh token with the provided data and expiration time.

        :param data: A dictionary containing the claims (payload) to be included in the refresh token.
        :type data: dict
        :param expires_delta: The expiration time in seconds for the refresh token. If not provided,
                               the token will expire in 7 days by default.
        :type expires_delta: Optional[float]
        :return: The encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decodes and validates a refresh token to retrieve.

        :param refresh_token: The refresh token to decode and validate.
        :type refresh_token: str
        :return: The email address associated with the refresh token if valid.
        :rtype: str
        :raises HTTPException: If the token is invalid or its scope is incorrect.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Retrieves the current authenticated user based on the provided access token.

        :param token: The access token used for authentication.
        :type token: str
        :param db: The database session used to query user information.
        :type db: Session
        :return: The user associated with the token if valid.
        :rtype: User
        :raises HTTPException: If the token is invalid or the user does not exist.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict):
        """
        Creates an email verification token for the provided data.

        :param data: A dictionary containing the data to be included in the email verification token.
        :type data: dict
        :return: The encoded JWT email verification token.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Decodes the provided email verification token and extracts the email.

        :param token: The email verification token to decode.
        :type token: str
        :return: The email address associated with the provided token.
        :rtype: str
        :raises HTTPException: If the token is invalid or cannot be decoded.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
