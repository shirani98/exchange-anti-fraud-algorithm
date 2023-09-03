import os
import random
import faker
from faker import Faker
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")
import django

django.setup()

from transaction.models import UserTransaction, ExternalTransaction

fake = Faker()


def generate_fake_transactions(model_class, num_records):
    for _ in range(num_records):
        end_time = timezone.now() - timedelta(days=7)
        created_at = fake.date_time_between(
            start_date=end_time, end_date=timezone.now()
        )
        amount = random.uniform(1, 1000)
        user_id = random.choice(
            [
                "4db00bc8-3e2c-4443-9070-77c2810dba5e",
                "52b8f76b-8296-4e18-a4c5-c0217b98e616",
                "1823f451-7052-434b-9401-068f305835ab",
                "f3bf10b3-b8af-4374-b910-27ee0b016d19",
            ]
        )
        wallet_id = random.uniform(1, 1000)
        type = random.choice([model_class.DEPOSIT, model_class.WITHDRAWAL])

        if model_class is ExternalTransaction:
            model_class.objects.create(
                created_at=created_at,
                amount=amount,
                user_id=user_id,
                type=type,
                wallet_id=wallet_id,
            )
        else:
            model_class.objects.create(
                created_at=created_at, amount=amount, user_id=user_id, type=type
            )


if __name__ == "__main__":
    num_user_transactions = 100000
    num_external_transactions = 100000

    generate_fake_transactions(UserTransaction, num_user_transactions)
    generate_fake_transactions(ExternalTransaction, num_external_transactions)
