# account/users/serializers.py
from rest_framework import serializers
from inventory.models import SimCard
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from utils.validators import validate_sim_number


class SimCardChargeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=0, help_text=_("charge amount in Toman"))
    simcard_number = serializers.CharField(
        help_text=_("mobile number to charge balance"), validators=[validate_sim_number]
    )

    def validate_amount(self, value):
        if value < Decimal("1000"):
            raise serializers.ValidationError(_("minimum charge amount is 1,000 Toman"))
        return value

    def validate_simcard_number(self, value):
        if not SimCard.objects.filter(number=value).exists():
            raise serializers.ValidationError(_("sim card with this number does not exist"))
        return value
