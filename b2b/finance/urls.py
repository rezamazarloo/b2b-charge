from django.urls import path
from .views import CreditRequestCreateView

app_name = "finance"

urlpatterns = [
    path("credit-requests/", CreditRequestCreateView.as_view(), name="credit-requests"),
]
