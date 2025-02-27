from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user by specified email.

    :param email: The email to search by.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: A user.
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a user with specified body parameters.

    :param body: The data to create user.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: A user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates refresh token for specified user.

    :param user: The user whose refresh token is being updated.
    :type user: User
    :param token: Token to be updated.
    :type token: Optional[str]
    :param db: The database session.
    :type db: Session
    :return: Nothing.
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirms the user's account creation by email.

    :param email: Email by which the user will be searched.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: Nothing.
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Updates user's avatar.

    :param email: Email by which the user will be searched.
    :type email: str
    :param url: Avatar image url.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: a User with new profile image.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
