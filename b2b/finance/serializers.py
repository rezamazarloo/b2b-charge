from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from .models import CreditRequest


class CreditRequestSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[
            MinValueValidator(1000, message="حداقل مبلغ قابل درخواست 1,000 تومان است"),
            MaxValueValidator(100000000, message="حداکثر مبلغ قابل درخواست 100,000,000 تومان است"),
        ],
    )

    class Meta:
        model = CreditRequest
        fields = ["id", "amount", "status", "created_at"]
        read_only_fields = ["id", "status", "is_processed", "created_at", "updated_at"]
