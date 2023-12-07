from celery import shared_task
import logging
import requests
import json
from django.core.serializers import deserialize
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)
from ..celery_services import celery_app
from stock_home.models import Users, StockData, Transaction
from stock_home.serializers import TransactionSerializer


@celery_app.task
def save_transaction(payload):
    print(payload)
    user_id = payload['user_id']
    ticker = payload['ticker']
    transaction_type = payload['transaction_type']
    transaction_volume = payload['transaction_volume']
    transaction_price = payload['transaction_price']
    user = Users.objects.get(id=user_id)
    stock = StockData.objects.get(ticker=ticker)

    if user.initial_balance >= stock.open_price and transaction_type == 'buy':
        user.initial_balance -= stock.open_price
    elif transaction_type == 'sell':
        user.initial_balance += stock.open_price
    user.save()

    transaction = Transaction.objects.create(
        user=user,
        stock_data=stock,
        transaction_type=transaction_type,
        transaction_volume=transaction_volume,
        transaction_price=transaction_price
    )
    return Response(status=status.HTTP_201_CREATED)

