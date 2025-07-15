# account/users/serializers.py
from rest_framework import serializers
from inventory.models import SimCard
from decimal import Decimal
from .validators import validate_sim_number


class SimCardChargeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=0, help_text="مبلغ شارژ به تومان")
    simcard_number = serializers.CharField(help_text="شماره موبایل جهت افزایش شارژ", validators=[validate_sim_number])

    def validate_amount(self, value):
        if value < Decimal("1000"):
            raise serializers.ValidationError("حداقل مبلغ شارژ 1000 تومان است.")
        return value

    def validate_simcard_number(self, value):
        if not SimCard.objects.filter(number=value).exists():
            raise serializers.ValidationError("شماره سیم کارت یافت نشد.")
        return value
