import unittest
from unittest.mock import MagicMock, patch
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)
from src.database.models import User
from src.schemas import UserModel
from sqlalchemy.orm import Session


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

        self.user_data = UserModel(
            username="test_user",
            email="test@example.com",
            password="123456",
        )

        self.existing_user = User(
            id=1,
            username="test_user",
            email="test@example.com",
            password="12345",
            avatar="test_avatar_url",
            refresh_token="test_refresh_token",
            confirmed=True,
        )

    def tearDown(self):
        self.session = None
        self.user_data = None
        self.existing_user = None

    async def test_get_user_by_email(self):
        self.session.query.return_value.filter.return_value.first.return_value = self.existing_user

        result = await get_user_by_email("test@example.com", self.session)
        self.assertEqual(result, self.existing_user)
        self.assertEqual(result.email, "test@example.com")
        self.session.query.assert_called_once_with(User)
        self.session.query().filter.assert_called_once()
        self.session.query().filter().first.assert_called_once()

    @patch('src.repository.users.Gravatar')
    async def test_create_user(self, mock_gravatar):
        mock_gravatar.return_value.get_image.return_value = "new_avatar_url"
        self.session.add = MagicMock()
        self.session.commit = MagicMock()
        self.session.refresh = MagicMock()

        result = await create_user(self.user_data, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, "test@example.com")
        self.assertEqual(result.avatar, "new_avatar_url")
        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

    async def test_update_token(self):
        new_token = "new_refresh_token"
        self.session.commit = MagicMock()
        await update_token(self.existing_user, new_token, self.session)
        self.assertEqual(self.existing_user.refresh_token, new_token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        self.session.query.return_value.filter.return_value.first.return_value = self.existing_user
        self.existing_user.confirmed = False
        await confirmed_email("test@example.com", self.session)
        self.assertTrue(self.existing_user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        new_avatar_url = "new_avatar_url"
        self.session.query.return_value.filter.return_value.first.return_value = self.existing_user
        result = await update_avatar("test@example.com", new_avatar_url, self.session)
        self.assertEqual(result.avatar, new_avatar_url)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
