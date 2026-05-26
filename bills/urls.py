from django.urls import path
from .views import BillsListView, BillHistoryView, RechargeHistoryView, TravelHistoryView

urlpatterns = [
    path('bills/', BillsListView.as_view(), name='bills-list'),
    path('bills/history/', BillHistoryView.as_view(), name='bill-history'),
    path('recharge/history/', RechargeHistoryView.as_view(), name='recharge-history'),
    path('travel/history/', TravelHistoryView.as_view(), name='travel-history'),
]