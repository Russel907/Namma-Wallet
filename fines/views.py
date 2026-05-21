from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from decouple import config

class CheckFinesView(APIView):
    def post(self, request):
        vehicle_number = request.data.get('vehicle_number')

        if not vehicle_number:
            return Response(
                {"error": "Vehicle number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        vehicle_number = vehicle_number.strip().upper()

        if len(vehicle_number) < 6:
            return Response(
                {"error": "Enter a valid vehicle number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            api_key = config('KWIKAPI_KEY', default=None)

            if not api_key:
                return Response(
                    {"error": "Service not configured. Please try again later."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            url = "https://www.kwikapi.com/api/v1/echallan"
            payload = {
                "api_key": api_key,
                "vehicle_number": vehicle_number
            }
            response = requests.post(url, data=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return Response({
                    "vehicle_number": vehicle_number,
                    "fines": data
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to fetch fines. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except requests.Timeout:
            return Response(
                {"error": "Request timed out. Please try again."},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.ConnectionError:
            return Response(
                {"error": "Network error. Please check your connection."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )