from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.database.models import Contact
from src.schemas import ContactResponse, ContactUpdate, ContactModel, ContactBase

async def read_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()

async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(name=body.name, surname=body.surname, email=body.email, phone=body.phone, birthday=body.birthday,
                      description=body.description)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def get_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    return contact

async def update_contact(contact_id: int, body: ContactUpdate, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.description = body.description

        db.commit()
    return contact

async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def search_contacts( db: Session, name: Optional[str], surname: Optional[str], email: Optional[str]) -> List[Contact] | None:
    query = db.query(Contact)
    if name:
        query = query.filter(Contact.name == name)
    if surname:
        query = query.filter(Contact.surname == surname)
    if email:
        query = query.filter(Contact.email == email)
    contacts = query.all()
    return contacts

async def read_birthdays(db: Session, days: int) -> List[Contact] | None:
    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    contacts = db.query(Contact).filter(
        Contact.birthday >= today,
        Contact.birthday <= end_date
    ).all()

    return contacts
