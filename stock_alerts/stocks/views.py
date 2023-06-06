from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import viewsets


from stocks.models import (
    DELETED,
    Stocks,
    UserStockAlerts
)
from .serializers import (
    StocksSerializer, 
    UserSerializer, 
    UserStockAlertsSerializer
)


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    # renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class StocksListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = StocksSerializer
    queryset = Stocks.objects.all()



class UserStocksAlertsView(viewsets.ModelViewSet):
    serializer_class = UserStockAlertsSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['stock', 'desired_price']

    def get_queryset(self):
        """
        This view should return a list of all the alerts set by currently authenticated user.
        """
        user = self.request.user
        return UserStockAlerts.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.pk
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk, *args, **kwargs):
        user_stock_alert = UserStockAlerts.objects.get(pk=pk)
        if user_stock_alert.user != request.user:
            # Something fishy. Return `Unauthorized`
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_stock_alert.status = DELETED
        user_stock_alert.save()
        return Response('Stock Alert Deleted Successfully', status=status.HTTP_204_NO_CONTENT)

    # With auth: cache requested url for each user for 10 mins
    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_headers("Authorization",))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)