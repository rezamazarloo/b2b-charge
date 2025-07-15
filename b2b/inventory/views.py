# account/users/views.py
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import SimCard
from finance.models import TransactionHistory
from .serializers import SimCardChargeSerializer

User = get_user_model()


class SimCardChargeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimCardChargeSerializer

    def post(self, request, *args, **kwargs):
        serializer = SimCardChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        simcard_number = serializer.validated_data["simcard_number"]

        try:
            with transaction.atomic():
                # Lock the user and simcard to prevent race conditions
                user = User.objects.select_for_update().get(pk=request.user.pk)
                simcard = SimCard.objects.select_for_update().filter(number=simcard_number).first()

                if user.balance < amount:
                    raise ValidationError({"amount": "موجودی حساب کافی نیست."})

                # Update user balance
                user.balance -= amount
                user.save(update_fields=["balance"])

                # Update simcard balance
                simcard.balance += amount
                simcard.save(update_fields=["balance"])

                # Create transaction history
                TransactionHistory.objects.create(
                    seller=user, simcard=simcard, amount=amount, type=TransactionHistory.TypeChoices.SIMCARD_CHARGE
                )

                return Response(
                    {
                        "message": "شماره سیم کارت با موفقیت شارژ شد.",
                        "simcard_number": simcard.number,
                        "user_balance": user.balance,
                        "simcard_balance": simcard.balance,
                    },
                    status=status.HTTP_200_OK,
                )

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
