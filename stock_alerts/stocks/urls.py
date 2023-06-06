from django.urls import path
from rest_framework.routers import DefaultRouter
from stocks import views

router = DefaultRouter()
router.register(r'user-stock-alerts', views.UserStocksAlertsView, basename='user-stock-alert')

urlpatterns = [
    path(r'user', views.UserRetrieveUpdateAPIView.as_view(), name="user-update"),
    path(r'stocks', views.StocksListView.as_view(), name="stocks"),
]

urlpatterns += router.urls