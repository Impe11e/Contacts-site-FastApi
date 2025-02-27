from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactUpdate, ContactModel, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a list of contacts for the current user with specified pagination parameters.

    :param skip: The number of contacts to skip. Default is 0.
    :type skip: int
    :param limit: The maximum number of contacts to return. Default is 100, but can be adjusted.
    :type limit: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: A list of contacts belonging to the current user.
    :rtype: List[ContactResponse]
    :raises HTTPException: If an error occurs while fetching contacts from the database.
    """
    contacts = await repository_contacts.read_contacts(skip, limit, current_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 5 requests per minute', dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new contact for the currently authenticated user.
    The number of requests allowed per minute is limited to 5.

    :param body: The contact data to create.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: The created contact information.
    :rtype: ContactResponse
    :raises HTTPException: If an error occurs while creating the contact.
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a specific contact for the currently authenticated user by contact ID.
    The number of requests allowed per minute is limited to 10.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: The requested contact information.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found (404 Not Found).
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates an existing contact for the currently authenticated user by contact ID.
    The number of requests allowed per minute is limited to 5.

    :param body: The contact data to update (including the contact's name, surname, email, etc.).
    :type body: ContactUpdate
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: The updated contact information.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found (404 Not Found).
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Deletes a contact for the currently authenticated user by contact ID.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: The deleted contact information.
    :rtype: ContactResponse
    :raises HTTPException: If the contact is not found (404 Not Found).
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/search/", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def search_contacts(current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db),
                          name: str = Query(None, description="First name of the contact", max_length=50),
                          surname: str = Query(None, description="Surname of the contact", max_length=150),
                          email: str = Query(None, description="Email of the contact", max_length=255)):
    """
    Searches for contacts for the currently authenticated user based on provided search criteria.
    The number of requests allowed per minute is limited to 5.

    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :param name: The first name of the contact to search for.
    :type name: str
    :param surname: The surname of the contact to search for.
    :type surname: str
    :param email: The email address of the contact to search for.
    :type email: str
    :return: A list of contacts matching the search criteria.
    :rtype: List[ContactResponse]
    :raises HTTPException: If no contacts are found (404 Not Found).
    """
    contacts = await repository_contacts.search_contacts(current_user, db, name, surname, email)
    if contacts is None:
        return {"message": "No contacts found"}
    return contacts


@router.get("/birthdays/", response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def read_birthdays(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db),
                         days: int = Query(7, ge=1, le=365, description="Number of days ahead to check birthdays")):
    """
    Retrieves a list of contacts with upcoming birthdays for the currently authenticated user within a specified
    number of days. The number of requests allowed per minute is limited to 5.

    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :param days: The number of days ahead to check birthdays. Defaults to 7 days.
    :type days: int
    :return: A list of contacts with upcoming birthdays within the specified range.
    :rtype: List[ContactResponse]
    :raises HTTPException: If no contacts have birthdays within the specified period (404 Not Found).
    """
    contacts = await repository_contacts.read_birthdays(db, current_user, days)
    if contacts is None:
        return {"message": "No birthdays found in this period"}
    return contacts
