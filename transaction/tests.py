from django.test import TestCase, override_settings
from .models import UserTransaction
from django.contrib.auth.models import User
import datetime


class FroudTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="723cd066-9f50-4cb9-a9e2-c0f603760b66",
            password="testpassword",
            email="testuser@example.com",
        )

    def test_user_without_any_transaction(self):
        result = UserTransaction.check_user_froud(self.user.username)
        self.assertTrue(result)

    def test_user_wit_before_48_hours_ago_transaction(self):
        UserTransaction.objects.create(
            amount=15000000,
            user_id=self.user.username,
            type=UserTransaction.DEPOSIT,
            created_at=datetime.datetime.now() - datetime.timedelta(days=4),
        )
        result = UserTransaction.check_user_froud(self.user.username)
        self.assertTrue(result)

    def test_user_wit_after_48_hours_ago_transaction(self):
        UserTransaction.objects.create(
            amount=15000000,
            user_id=self.user.username,
            type=UserTransaction.DEPOSIT,
            created_at=datetime.datetime.now() - datetime.timedelta(days=1),
        )
        result = UserTransaction.check_user_froud(self.user.username)
        self.assertFalse(result)

    def test_transaction_under_limit_amount(self):
        UserTransaction.objects.create(
            amount=150000,
            user_id=self.user.username,
            type=UserTransaction.DEPOSIT,
            created_at=datetime.datetime.now() - datetime.timedelta(days=1),
        )
        result = UserTransaction.check_user_froud(self.user.username)
        self.assertTrue(result)

    def test_transaction_over_limit_amount(self):
        UserTransaction.objects.create(
            amount=300000,
            user_id=self.user.username,
            type=UserTransaction.DEPOSIT,
            created_at=datetime.datetime.now() - datetime.timedelta(days=1),
        )
        result = UserTransaction.check_user_froud(self.user.username)
        self.assertFalse(result)

    def test_over_max_percentage_change_transaction(self):
        UserTransaction.objects.create(
            amount=1000000,
            user_id=self.user.username,
            type=UserTransaction.DEPOSIT,
            created_at=datetime.datetime.now() - datetime.timedelta(days=5),
        )
        UserTransaction.objects.create(
            amount=20000000,
            user_id=self.user.username,
            type=UserTransaction.DEPOSIT,
            created_at=datetime.datetime.now() - datetime.timedelta(days=1),
        )
        result = UserTransaction.check_user_froud(self.user.username)
        self.assertFalse(result)

    @override_settings(MAXIMUM_CHANGE_PERCENTAGE=30)
    def test_under_max_percentage_change_transaction(self):
        UserTransaction.objects.create(
            amount=1000000,
            user_id=self.user.username,
            type=UserTransaction.DEPOSIT,
            created_at=datetime.datetime.now() - datetime.timedelta(days=5),
        )
        UserTransaction.objects.create(
            amount=20000000,
            user_id=self.user.username,
            type=UserTransaction.DEPOSIT,
            created_at=datetime.datetime.now() - datetime.timedelta(days=1),
        )
        result = UserTransaction.check_user_froud(self.user.username)
        self.assertTrue(result)
