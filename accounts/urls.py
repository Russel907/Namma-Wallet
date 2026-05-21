from django.urls import path
from .views import SendOTPView, VerifyOTPView, UserProfileView, LogoutView, AddressListCreateView, AddressDetailView, LinkedCardListCreateView, LinkedCardDetailView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('user/addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('user/cards/', LinkedCardListCreateView.as_view(), name='card-list-create'),
    path('user/cards/<int:pk>/', LinkedCardDetailView.as_view(), name='card-detail'),

]