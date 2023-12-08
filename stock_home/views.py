from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from stock_home.serializers import UserSerializer, StockDataSerializer, TransactionSerializer
from stock_home.models import Users, StockData, Transaction
from stock_home.celery_services.celery_tasks.celery_tasks import save_transaction
from django.core.cache import cache


# Create your views here.
class UsersViewSet(ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of YourModel instances.",
        # request_body=UserSerializer,
        responses={
            200: UserSerializer(many=True),
            # Add other response codes and descriptions as needed
        },
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="User ID",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of Users.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create a new instance of Users.
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        balance = serializer.validated_data["initial_balance"]
        Users.objects.create(username=username, initial_balance=balance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve details of a user by user_id.
        """
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

    @swagger_auto_schema(responce_body=StockDataSerializer)
    def list(self, request, *args, **kwargs):
        return super(StockDataViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=StockDataSerializer)
    def create(self, request, *args, **kwargs):
        return super(StockDataViewSet, self).create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        user_id = self.request.query_params.get('user_id')
        if not user_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Users.objects.get(username=user_id)


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @swagger_auto_schema(request_body=TransactionSerializer)
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
