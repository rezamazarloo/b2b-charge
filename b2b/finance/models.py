from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from inventory.models import SimCard

User = get_user_model()


class CreditRequest(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "در انتظار تایید"
        COMPLETE = "complete", "تکمیل شده"
        REJECT = "reject", "رد شده"

    user = models.ForeignKey(User, verbose_name="کاربر", on_delete=models.CASCADE, related_name="user_credit_requests")
    amount = models.DecimalField(verbose_name="مبلغ درخواستی", max_digits=12, decimal_places=0, help_text="تومان")
    status = models.CharField(
        verbose_name="وضعیت درخواست", max_length=8, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    is_processed = models.BooleanField(verbose_name="وضعیت پردازش", default=False)
    created_at = models.DateTimeField(verbose_name="تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "درخواست اعتبار"
        verbose_name_plural = "درخواست های اعتبار"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"id({self.pk}) - {self.amount} - {self.get_status_display()}"


class Transaction(models.Model):
    class TypeChoices(models.TextChoices):
        BALANCE_TOP_UP = "balance_top_up", "افزایش موجودی حساب"
        SIMCARD_CHARGE = "simcard_charge", "شارژ سیم کارت"

    seller = models.ForeignKey(
        User, verbose_name="کاربر فروشنده", on_delete=models.CASCADE, related_name="seller_transactions"
    )
    simcard = models.ForeignKey(
        SimCard,
        on_delete=models.SET_NULL,
        verbose_name="شماره سیم کارت",
        related_name="simcard_transactions",
        null=True,
        blank=True,
        default=None,
    )
    credit_request = models.OneToOneField(
        CreditRequest,
        on_delete=models.SET_NULL,
        verbose_name="درخواست اعتبار",
        related_name="credit_request_transaction",
        null=True,
        blank=True,
        default=None,
    )
    amount = models.DecimalField(verbose_name="مبلغ", max_digits=12, decimal_places=0, help_text="تومان")
    type = models.CharField(verbose_name="نوع تراکنش", max_length=15, choices=TypeChoices.choices)
    created_at = models.DateTimeField(verbose_name="تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="تاریخ بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش ها"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"seller({self.seller.pk}) - {self.get_type_display()} - {self.amount}"
