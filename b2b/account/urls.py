from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

app_name = "account"

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="auth-jwt-token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="auth-jwt-token-refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="auth-jwt-token-verify"),
]
