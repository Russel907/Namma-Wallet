from django.urls import path
from .views import BillsListView

urlpatterns = [
    path('bills/', BillsListView.as_view(), name='bills-list'),
]