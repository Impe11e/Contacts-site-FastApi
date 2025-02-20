from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactUpdate, ContactModel, ContactResponse
from src.repository import contacts as repository_contacts


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.read_contacts(skip, limit, db)
    return contacts


@router.post("/", response_model=ContactResponse)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(db: Session = Depends(get_db),
    name: str = Query(None, description="First name of the contact", max_length=50),
    surname: str = Query(None, description="Surname of the contact", max_length=150),
    email: str = Query(None, description="Email of the contact", max_length=255)):
    contacts = await repository_contacts.search_contacts(db, name, surname, email)
    if contacts is None:
        return {"message": "No contacts found"}
    return contacts

@router.get("/birthdays/", response_model=List[ContactResponse])
async def read_birthdays(db: Session = Depends(get_db), days: int = Query(7, ge=1, le=365, description="Number of days ahead to check birthdays")):
    contacts = await repository_contacts.read_birthdays(db, days)
    if contacts is None:
        return {"message": "No birthdays found in this period"}
    return contacts
