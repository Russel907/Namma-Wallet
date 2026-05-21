from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer

class WalletBalanceView(APIView):
    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionHistoryView(APIView):
    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        transactions = Transaction.objects.filter(
            wallet=wallet
        ).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response({
            "wallet_balance": wallet.balance,
            "transactions": serializer.data
        }, status=status.HTTP_200_OK)

class HomeScreenView(APIView):
    def get(self, request):
        try:
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            recent_transactions = Transaction.objects.filter(
                wallet=wallet
            ).order_by('-created_at')[:5]

            return Response({
                "user": {
                    "name": request.user.first_name or request.user.mobile_number,
                    "mobile_number": request.user.mobile_number,
                },
                "wallet_balance": wallet.balance,
                "recent_transactions": TransactionSerializer(recent_transactions, many=True).data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )