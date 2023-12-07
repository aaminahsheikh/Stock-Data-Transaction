from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response

from stock_home.serializers import UserSerializer, StockDataSerializer, TransactionSerializer
from stock_home.models import Users, StockData, Transaction
from stock_home.celery_services.celery_tasks.celery_tasks import save_transaction
from django.core.cache import cache


# Create your views here.
class UsersViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def list(self, request):
        return Response(self.serializer_class(self.queryset, many=True).data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        balance = serializer.validated_data["balance"]
        Users.objects.create(username=username, initial_balance=balance)
        return Response(status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = cache.get(f'user_{user_id}')
        if user is None:
            user = self.get_object()
            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            cache.set(f'user_{user_id}', user)

        serializer = self.get_serializer(user)
        print("===========", cache.get(f'user_{user_id}'))
        return Response(serializer.data)


class StockDataViewSet(ModelViewSet):
    queryset = StockData.objects.all()
    serializer_class = StockDataSerializer

    def list(self, request):
        return Response(self.serializer_class(self.queryset, many=True).data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer_valid = serializer.validated_data
        ticker = serializer_valid["ticker"]
        open_price = serializer_valid["open_price"]
        close_price = serializer_valid["close_price"]
        high = serializer_valid["high"]
        low = serializer_valid["low"]
        volume = serializer_valid["volume"]

        StockData.objects.create(ticker=ticker, open_price=open_price, close_price=close_price, high=high, low=low,
                                 volume=volume)
        return Response(status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        user_id = self.request.query_params.get('user_id')
        if not user_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Users.objects.get(username=user_id)


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        ticker = request.data.get('ticker')
        user = Users.objects.get(id=user_id)
        stock = StockData.objects.get(ticker=ticker)

        if not user or not stock:
            return Response("Invalid data!", status=status.HTTP_400_BAD_REQUEST)

        if user.initial_balance < stock.open_price:
            return Response("Low balance!", status=status.HTTP_400_BAD_REQUEST)

        save_transaction.delay(request.data)
        print('working!!!...')
        return Response(status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        return Transaction.objects.filter(user=user_id)
