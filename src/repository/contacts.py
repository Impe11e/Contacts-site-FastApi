from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Contact, User
from src.schemas import ContactResponse, ContactUpdate, ContactModel, ContactBase

async def read_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()

async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a specific user with data entered by this user.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param user: The user to create contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: a created contact.
    :rtype: Contact
    """
    contact = Contact(name=body.name, surname=body.surname, email=body.email, phone=body.phone, birthday=body.birthday,
                      description=body.description, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def get_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to receive.
    :type contact_id: int
    :param user: The user to get contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: a requested contact or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    return contact

async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The data for the contact to update.
    :type body: ContactUpdate
    :param user: The user to update contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: an updated contact or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.name = (body.name,)
        contact.surname = (body.surname,)
        contact.email = (body.email,)
        contact.phone = (body.phone,)
        contact.birthday = (body.birthday,)
        contact.description = body.description

        db.commit()
    return contact

async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to remove contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Removed contact or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def search_contacts(user: User, db: Session, name: Optional[str], surname: Optional[str], email: Optional[str]) -> List[Contact] | None:
    """
    Searches for contacts for specified users based on the specified parameters.

    :param user: The user to search contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :param name: The name of the searched contact(s).
    :type name: Optional[str]
    :param surname: The surname of the searched contact(s).
    :type surname: Optional[str]
    :param email: The email of the searched contact.
    :type email: Optional[str]
    :return: List of searched contacts or None if they do not found.
    :rtype: List[Contact] | None
    """
    query = db.query(Contact)
    if name:
        query = query.filter(and_(Contact.name == name, Contact.user_id == user.id))
    if surname:
        query = query.filter(and_(Contact.surname == surname, Contact.user_id == user.id))
    if email:
        query = query.filter(and_(Contact.email == email, Contact.user_id == user.id))
    contacts = query.all()
    return contacts

async def read_birthdays(db: Session, user: User, days: int) -> List[Contact] | None:
    """
    Searches for users whose birthdays are within the next days specified by the user.

    :param db: The database session.
    :type db: Session
    :param user: The user to search contacts for.
    :type user: User
    :param days: Number of days to search for birthdays.
    :type days: int
    :return: List of searched contacts or None if they do not found.
    :rtype: List[Contact] | None
    """
    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    contacts = db.query(Contact).filter(and_(
        Contact.birthday >= today,
        Contact.birthday <= end_date,
        Contact.user_id == user.id
    )).all()

    return contacts
