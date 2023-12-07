import uuid
from django.db import models
from stock_home.base.base_models import BaseModel
# Create your models here.


class Users(BaseModel):
    username = models.CharField(max_length=250, null=False, blank=False)
    initial_balance = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.username} - {self.id}"


class StockData(BaseModel):
    ticker = models.CharField(max_length=10)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()

    def __str__(self):
        return f"{self.ticker} - {self.volume}"


class Transaction(BaseModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    stock_data = models.ForeignKey(StockData, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    transaction_volume = models.IntegerField()
    transaction_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.stock_data}"
