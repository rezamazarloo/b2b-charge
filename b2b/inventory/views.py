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
from django.utils.translation import gettext_lazy as _
from .serializers import SimCardChargeSerializer
from utils.logger import SimCardChargeLogger

User = get_user_model()


class SimCardChargeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimCardChargeSerializer

    def post(self, request, *args, **kwargs):
        serializer = SimCardChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount"]
        simcard_number = serializer.validated_data["simcard_number"]
        user_id = request.user.pk

        SimCardChargeLogger.log_start(user_id, amount, simcard_number)
        try:
            with transaction.atomic():
                # Lock the user and simcard to prevent race conditions
                user = User.objects.select_for_update().get(pk=user_id)
                simcard = SimCard.objects.select_for_update().filter(number=simcard_number).first()

                if user.balance < amount:
                    raise ValidationError({"amount": _("insufficient account balance")})

                # Update user balance
                user.balance -= amount
                user.save(update_fields=["balance"])

                # Update simcard balance
                simcard.balance += amount
                simcard.save(update_fields=["balance"])

                # Create transaction history
                transaction_history = TransactionHistory.objects.create(
                    seller=user, simcard=simcard, amount=amount, type=TransactionHistory.TypeChoices.SIMCARD_CHARGE
                )

                SimCardChargeLogger.log_success(
                    user_id, amount, simcard_number, user.balance, simcard.balance, transaction_history.pk
                )

                return Response(
                    {
                        "message": _("successfully charged simcard"),
                        "simcard_number": simcard.number,
                        "user_balance": user.balance,
                        "simcard_balance": simcard.balance,
                    },
                    status=status.HTTP_200_OK,
                )

        except ValidationError as e:
            SimCardChargeLogger.log_validation_error(user_id, amount, simcard_number, e.detail)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            SimCardChargeLogger.log_system_error(user_id, amount, simcard_number, str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
