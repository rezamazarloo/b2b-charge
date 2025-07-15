from django.urls import path
from .views import CreditRequestCreateAPIView

app_name = "finance"

urlpatterns = [
    path("credit-requests/", CreditRequestCreateAPIView.as_view(), name="credit-requests-create"),
]
