from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import CreditRequest


class CreditRequestSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[
            MinValueValidator(1000, message=_("minimum amount is 1,000 Toman")),
            MaxValueValidator(100000000, message=_("maximum amount is 100,000,000 Toman")),
        ],
    )

    class Meta:
        model = CreditRequest
        fields = ["id", "amount", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]
