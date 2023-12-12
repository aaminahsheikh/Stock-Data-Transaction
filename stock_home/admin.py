from django.contrib import admin
from stock_home.models import Users, StockData, Transaction
# Register your models here.

admin.site.register(Users)
admin.site.register(StockData)
admin.site.register(Transaction)
