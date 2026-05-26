from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Bill, Recharge
from .serializers import BillSerializer, RechargeSerializer
from tickets.models import Ticket
from tickets.serializers import TicketSerializer

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

class BillHistoryView(APIView):
    def get(self, request):
        try:
            paid_bills = Bill.objects.filter(
                user=request.user,
                status='PAID'
            ).order_by('-created_at')
            return Response({
                "total_paid": paid_bills.count(),
                "bill_history": BillSerializer(paid_bills, many=True).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RechargeHistoryView(APIView):
    def get(self, request):
        try:
            recharges = Recharge.objects.filter(
                user=request.user
            ).order_by('-created_at')
            return Response({
                "total_recharges": recharges.count(),
                "recharge_history": RechargeSerializer(recharges, many=True).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TravelHistoryView(APIView):
    def get(self, request):
        try:
            travel = Ticket.objects.filter(
                user=request.user,
                status='USED'
            ).order_by('-created_at')
            return Response({
                "total_trips": travel.count(),
                "travel_history": TicketSerializer(travel, many=True).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )