from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Bill
from .serializers import BillSerializer

class BillsListView(APIView):
    def get(self, request):
        try:
            bills = Bill.objects.filter(user=request.user).order_by('-created_at')
            pending = bills.filter(status='PENDING')
            paid = bills.filter(status='PAID')
            overdue = bills.filter(status='OVERDUE')
            return Response({
                "total_pending": pending.count(),
                "total_paid": paid.count(),
                "total_overdue": overdue.count(),
                "pending_bills": BillSerializer(pending, many=True).data,
                "paid_bills": BillSerializer(paid, many=True).data,
                "overdue_bills": BillSerializer(overdue, many=True).data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )