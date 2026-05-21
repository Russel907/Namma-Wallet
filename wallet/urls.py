from django.urls import path
from .views import WalletBalanceView, TransactionHistoryView, HomeScreenView

urlpatterns = [
    path('wallet/balance/', WalletBalanceView.as_view(), name='wallet-balance'),
    path('wallet/transactions/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('home/', HomeScreenView.as_view(), name='home-screen'),
]