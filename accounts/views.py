from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, OTP
from .utils import send_otp_via_messagecentral, verify_otp_via_messagecentral
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import UserProfileSerializer

from .models import User, OTP, Address, LinkedCard, Vehicle
from .serializers import UserProfileSerializer, AddressSerializer, LinkedCardSerializer, VehicleSerializer

RESEND_COOLDOWN_SECONDS = 30
OTP_TTL_SECONDS = 600  # 10 minutes

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = request.data.get('mobile_number')

        if not mobile_number:
            return Response(
                {"error": "Mobile number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(mobile_number) != 10:
            return Response(
                {"error": "Enter a valid 10 digit mobile number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cooldown check
        last_otp = OTP.objects.filter(
            mobile_number=mobile_number,
            is_used=False
        ).order_by('-created_at').first()

        if last_otp:
            seconds_passed = (timezone.now() - last_otp.created_at).total_seconds()
            if seconds_passed < RESEND_COOLDOWN_SECONDS:
                retry_after = int(RESEND_COOLDOWN_SECONDS - seconds_passed)
                return Response(
                    {
                        "error": "Please wait before requesting another OTP.",
                        "retry_after_seconds": retry_after
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        # Send OTP via MessageCentral
        ok, provider_resp = send_otp_via_messagecentral(mobile_number)

        if not ok:
            return Response(
                {"error": "Failed to send OTP. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Save OTP record with MessageCentral's verification ID
        otp_obj = OTP.objects.create(
            mobile_number=mobile_number,
            otp_code='mc_generated'
        )

        data = provider_resp.get("data") if isinstance(provider_resp, dict) else None
        if data:
            otp_obj.provider_verification_id = data.get("verificationId")
            otp_obj.provider_transaction_id = data.get("transactionId")
            otp_obj.save()

        return Response(
            {
                "message": "OTP sent successfully",
                "expires_in": "10 minutes"
            },
            status=status.HTTP_200_OK
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        otp_code = request.data.get('otp_code')

        if not mobile_number or not otp_code:
            return Response(
                {"error": "Mobile number and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get latest unused OTP
        try:
            otp = OTP.objects.filter(
                mobile_number=mobile_number,
                is_used=False
            ).latest('created_at')
        except OTP.DoesNotExist:
            return Response(
                {"error": "No OTP found. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry
        expiry_time = otp.created_at + timedelta(seconds=OTP_TTL_SECONDS)
        if timezone.now() > expiry_time:
            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check verification ID exists
        if not otp.provider_verification_id:
            return Response(
                {"error": "Verification ID missing. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify OTP via MessageCentral
        ok, response = verify_otp_via_messagecentral(
            mobile_number=mobile_number,
            otp_code=otp_code,
            verification_id=otp.provider_verification_id
        )

        if not ok:
            return Response(
                {"error": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        # Get or create user
        user, created = User.objects.get_or_create(
            mobile_number=mobile_number,
            defaults={'username': mobile_number}
        )

        # Mark mobile as verified
        user.is_mobile_verified = True
        user.save()


        # Generate JWT tokens
        tokens = get_tokens_for_user(user)
        
        return Response({
            "message": "OTP verified successfully",
            "access": tokens['access'],
            "refresh": tokens['refresh'],
            "is_new_user": created
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

class AddressListCreateView(APIView):
    def get(self, request):
        # Get all addresses of logged in user
        addresses = Address.objects.filter(user=request.user).order_by('-created_at')
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            # If this is set as default, remove default from all other addresses
            if request.data.get('is_default'):
                Address.objects.filter(
                    user=request.user,
                    is_default=True
                ).update(is_default=False)
            serializer.save(user=request.user)
            return Response({
                "message": "Address saved successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    def delete(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
            address.delete()
            return Response(
                {"message": "Address deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Address.DoesNotExist:
            return Response(
                {"error": "Address not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
            serializer = AddressSerializer(address, data=request.data, partial=True)
            if serializer.is_valid():
                if request.data.get('is_default'):
                    Address.objects.filter(
                        user=request.user,
                        is_default=True
                    ).update(is_default=False)
                serializer.save()
                return Response({
                    "message": "Address updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Address.DoesNotExist:
            return Response(
                {"error": "Address not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class LinkedCardListCreateView(APIView):
    def get(self, request):
        cards = LinkedCard.objects.filter(
            user=request.user
        ).order_by('-created_at')
        serializer = LinkedCardSerializer(cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LinkedCardSerializer(data=request.data)
        if serializer.is_valid():
            # If this is set as default, remove default from others
            if request.data.get('is_default'):
                LinkedCard.objects.filter(
                    user=request.user,
                    is_default=True
                ).update(is_default=False)
            serializer.save(user=request.user)
            return Response({
                "message": "Card saved successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LinkedCardDetailView(APIView):
    def delete(self, request, pk):
        try:
            card = LinkedCard.objects.get(pk=pk, user=request.user)
            card.delete()
            return Response(
                {"message": "Card removed successfully"},
                status=status.HTTP_200_OK
            )
        except LinkedCard.DoesNotExist:
            return Response(
                {"error": "Card not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            card = LinkedCard.objects.get(pk=pk, user=request.user)
            serializer = LinkedCardSerializer(
                card,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                if request.data.get('is_default'):
                    LinkedCard.objects.filter(
                        user=request.user,
                        is_default=True
                    ).update(is_default=False)
                serializer.save()
                return Response({
                    "message": "Card updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except LinkedCard.DoesNotExist:
            return Response(
                {"error": "Card not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class VehicleListCreateView(APIView):
    def get(self, request):
        vehicles = Vehicle.objects.filter(
            user=request.user
        ).order_by('-created_at')
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            if request.data.get('is_default'):
                Vehicle.objects.filter(
                    user=request.user,
                    is_default=True
                ).update(is_default=False)
            serializer.save(user=request.user)
            return Response({
                "message": "Vehicle saved successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class VehicleDetailView(APIView):
    def delete(self, request, pk):
        try:
            vehicle = Vehicle.objects.get(pk=pk, user=request.user)
            vehicle.delete()
            return Response(
                {"message": "Vehicle deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Vehicle.DoesNotExist:
            return Response(
                {"error": "Vehicle not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            vehicle = Vehicle.objects.get(pk=pk, user=request.user)
            serializer = VehicleSerializer(
                vehicle,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                if request.data.get('is_default'):
                    Vehicle.objects.filter(
                        user=request.user,
                        is_default=True
                    ).update(is_default=False)
                serializer.save()
                return Response({
                    "message": "Vehicle updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Vehicle.DoesNotExist:
            return Response(
                {"error": "Vehicle not found"},
                status=status.HTTP_404_NOT_FOUND
            )