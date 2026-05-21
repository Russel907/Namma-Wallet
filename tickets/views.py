from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket
from .serializers import TicketSerializer
from django.utils import timezone

class TicketsListView(APIView):
    def get(self, request):
        try:
            today = timezone.now().date()
            active = Ticket.objects.filter(
                user=request.user,
                status='ACTIVE',
                travel_date__gte=today
            ).order_by('travel_date')

            used = Ticket.objects.filter(
                user=request.user,
                status='USED'
            ).order_by('-travel_date')

            expired = Ticket.objects.filter(
                user=request.user,
                status='EXPIRED'
            ).order_by('-travel_date')

            return Response({
                "active_tickets_count": active.count(),
                "active_tickets": TicketSerializer(active, many=True).data,
                "used_tickets": TicketSerializer(used, many=True).data,
                "expired_tickets": TicketSerializer(expired, many=True).data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )