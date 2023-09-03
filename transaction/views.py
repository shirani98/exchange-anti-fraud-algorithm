from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserTransaction
import time


class UserTransactionListView(APIView):
    def get(self, request, user_ids):
        result = UserTransaction.check_user_froud(user_id=user_ids)
        response_data = {
            "result": result,
        }
        return Response(response_data, status=status.HTTP_200_OK)
