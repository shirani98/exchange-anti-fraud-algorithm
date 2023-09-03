from django.db import models
import uuid
from django.db.models import Sum, F, Case, When, Count, IntegerField
from django.db.models.functions import Coalesce
import datetime
from django.conf import settings
from django.db import transaction


class BaseModel(models.Model):
    DEPOSIT = 1
    WITHDRAWAL = 2

    TRANSACTION_TYPE_CHOICES = (
        (DEPOSIT, "Deposit"),
        (WITHDRAWAL, "Withdrawal"),
    )

    amount = models.DecimalField(max_digits=100, decimal_places=0)
    user_id = models.UUIDField(default=uuid.uuid4, editable=False)
    type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField()

    class Meta:
        abstract = True

    @classmethod
    def get_deposit_amount_per_user(cls, user_id):
        pass

    @classmethod
    def get_withdrawal_count_per_user(cls, user_id):
        pass

    @classmethod
    def check_user_froud(cls, user_id):
        pass


class UserTransaction(BaseModel):
    @classmethod
    def check_user_froud(cls, user_id):
        transactions = cls.get_deposit_amount_per_user(user_id)
        print("*" * 80)
        print(transactions)
        if (
            not transactions["before_48_hours_ago"]
            and not transactions["after_48_hours_ago"]
        ):
            return True

        max_amount = (
            transactions["before_48_hours_ago"] * settings.MAXIMUM_CHANGE_PERCENTAGE
        )

        if (
            transactions["before_48_hours_ago"]
            and transactions["after_48_hours_ago"] < max_amount
        ):
            return True

        extrnal_count = ExternalTransaction.get_withdrawal_count_per_user(user_id)
        if (
            not transactions["before_48_hours_ago"]
            and transactions["after_48_hours_ago"] < 250000
            and extrnal_count <= 3
        ):
            return True
        return False

    @classmethod
    def get_deposit_amount_per_user(cls, user_id):
        last_48_hours_time = datetime.datetime.now() - datetime.timedelta(hours=48)
        with transaction.atomic():
            locked_rows = cls.objects.filter(
                user_id=user_id, type=UserTransaction.DEPOSIT
            ).select_for_update()
            return locked_rows.aggregate(
                before_48_hours_ago=Coalesce(
                    Sum(
                        Case(
                            When(created_at__lt=last_48_hours_time, then=F("amount")),
                            output_field=IntegerField(),
                        )
                    ),
                    0,
                ),
                after_48_hours_ago=Coalesce(
                    Sum(
                        Case(
                            When(created_at__gte=last_48_hours_time, then=F("amount")),
                            output_field=IntegerField(),
                        )
                    ),
                    0,
                ),
            )


class ExternalTransaction(BaseModel):
    wallet_id = models.IntegerField()

    @classmethod
    def get_withdrawal_count_per_user(cls, user_id):
        return cls.objects.filter(
            user_id=user_id, type=ExternalTransaction.WITHDRAWAL
        ).aggregate(total_amount=Count("amount"))["total_amount"]
