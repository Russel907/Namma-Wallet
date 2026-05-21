from django.urls import path
from .views import CheckFinesView

urlpatterns = [
    path('fines/check/', CheckFinesView.as_view(), name='check-fines'),
]