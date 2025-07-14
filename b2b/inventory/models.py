from django.db import models
from decimal import Decimal
from .validators import validate_sim_number


class SimCard(models.Model):
    class OperatorChoices(models.TextChoices):
        MTN = "mtn", "ایرانسل"
        MCI = "mci", "همراه اول"

    number = models.CharField(verbose_name="شماره موبایل", max_length=11, unique=True, validators=[validate_sim_number])
    operator = models.CharField(verbose_name="اپراتور شماره موبایل", max_length=3, choices=OperatorChoices.choices)
    balance = models.DecimalField(
        verbose_name="شارژ سیمکارت", max_digits=12, decimal_places=0, default=Decimal("0"), help_text="تومان"
    )
    created_at = models.DateTimeField(verbose_name="تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "سیم کارت"
        verbose_name_plural = "سیم کارت ها"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.number}"
