from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Contact, User
from src.schemas import ContactResponse, ContactUpdate, ContactModel, ContactBase

async def read_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()

async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    contact = Contact(name=body.name, surname=body.surname, email=body.email, phone=body.phone, birthday=body.birthday,
                      description=body.description, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def get_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    return contact

async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
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
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def search_contacts(user: User, db: Session, name: Optional[str], surname: Optional[str], email: Optional[str]) -> List[Contact] | None:
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
    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    contacts = db.query(Contact).filter(and_(
        Contact.birthday >= today,
        Contact.birthday <= end_date,
        Contact.user_id == user.id
    )).all()

    return contacts
