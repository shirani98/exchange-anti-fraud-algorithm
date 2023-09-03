from django.urls import path
from .views import UserTransactionListView

app_name = "transaction"


urlpatterns = [
    path(
        "api/user/<uuid:user_ids>/",
        UserTransactionListView.as_view(),
        name="user-transaction-list",
    ),
]
