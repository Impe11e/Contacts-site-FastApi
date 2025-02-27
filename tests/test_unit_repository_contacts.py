import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User, Contact
from src.schemas import ContactModel, ContactUpdate
from src.repository.contacts import (
    read_contacts,
    create_contact,
    get_contact,
    update_contact,
    remove_contact,
    search_contacts,
    read_birthdays,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    def tearDown(self):
        self.user = None
        self.session = None

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await read_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            name="Test",
            surname="User",
            email="test@gmail.com",
            phone="+380990000001",
            birthday="1999-01-01",
            description="test1"
        )
        result = await create_contact(body, self.user, self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.description, body.description)
        self.assertEqual(result.user_id, self.user.id)
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        body = ContactUpdate(name="Test2",
                             surname="User2",
                             email="test2@gmail.com",
                             description="test2",
                             phone="+380990000002",
                             )

        self.session.query().filter().first.return_value = self.session.query().filter().first()
        self.session.commit.return_value = None

        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)

        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.description, body.description)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(name="Test2",
                             surname="User2",
                             email="test2@gmail.com",
                             phone="+380990000002",
                             description="test2")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None

        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)

        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_search_contacts(self):
        user = self.user
        contacts = [
            Contact(id=2, user_id=user.id, name="John", surname="Doe", email="john@example.com", phone="+380990000004"),
            Contact(id=3, user_id=user.id, name="Jane", surname="Doe", email="jane@example.com", phone="+380990000003")
        ]

        self.session.query().filter().all.return_value = contacts

        result = await search_contacts(user=user, db=self.session, name="John", surname=None, email=None)

        self.assertEqual(result, contacts)
        self.session.query().filter.assert_called()

    async def test_read_birthdays(self):
        user = self.user
        today = datetime.now().date()
        end_date = today + timedelta(days=7)
        contacts = [
            Contact(id=1, user_id=user.id, name="Alice", surname="Smith", email="alice@example.com",
                    phone="+380990000005", birthday=today),
            Contact(id=2, user_id=user.id, name="Bob", surname="Brown", email="bob@example.com", phone="+380990000006",
                    birthday=end_date)
        ]

        self.session.query().filter().all.return_value = contacts

        result = await read_birthdays(db=self.session, user=user, days=7)

        self.assertEqual(result, contacts)
        self.session.query().filter.assert_called()


if __name__ == '__main__':
    unittest.main()
