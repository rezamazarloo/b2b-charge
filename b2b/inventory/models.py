from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


def validate_sim_number(value):
    """
    Validate that the SIM number starts with 09 and is exactly 11 characters long.
    """
    if not value.startswith("09"):
        raise ValidationError("SIM number must start with 09")

    if len(value) != 11:
        raise ValidationError("SIM number must be exactly 11 characters long")

    if not value.isdigit():
        raise ValidationError("SIM number must contain only digits")


class SimCard(models.Model):
    class OperatorChoices(models.TextChoices):
        MTN = "mtn", "ایرانسل"
        MCI = "mci", "همراه اول"

    number = models.CharField(verbose_name="شماره موبایل", max_length=11, unique=True, validators=[validate_sim_number])
    operator = models.CharField(verbose_name="اپراتور شماره موبایل", max_length=3, choices=OperatorChoices.choices)
    balance = models.DecimalField(verbose_name="موجودی سیمکارت", max_digits=12, decimal_places=0, default=Decimal("0"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "سیم کارت"
        verbose_name_plural = "سیم کارت ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number}"
