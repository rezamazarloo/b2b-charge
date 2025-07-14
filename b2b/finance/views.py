from rest_framework import generics, permissions
from .serializers import CreditRequestSerializer


class CreditRequestCreateView(generics.CreateAPIView):
    serializer_class = CreditRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Set the user to the current user automatically"""
        serializer.save(user=self.request.user)
