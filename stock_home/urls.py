from django.urls import path
from rest_framework import routers

from stock_home.views import UsersViewSet, StockDataViewSet, TransactionViewSet

app_name = 'stock_home'
router = routers.DefaultRouter()
router.register(r'users', UsersViewSet, basename="users")
router.register(r'stocks', StockDataViewSet, basename="stocks")
router.register(r'transactions', TransactionViewSet, basename="transactions")

urlpatterns = router.urls
