from django.urls import path
from .views import SimCardChargeAPIView

app_name = "inventory"

urlpatterns = [
    path("charge/", SimCardChargeAPIView.as_view(), name="simcard-charge"),
]
