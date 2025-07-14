from django.db import models, transaction
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

    def save(self, *args, **kwargs):
        if self._state.adding:
            # create object
            super().save(*args, **kwargs)
            return

        old_instance = CreditRequest.objects.only("status", "is_processed").filter(pk=self.pk).first()

        if (
            old_instance
            and old_instance.status == self.StatusChoices.PENDING
            and self.status == self.StatusChoices.COMPLETE
            and not old_instance.is_processed
        ):
            with transaction.atomic():
                locked_self = CreditRequest.objects.select_for_update().get(pk=self.pk)

                if (
                    locked_self.status == self.StatusChoices.PENDING
                    and self.status == self.StatusChoices.COMPLETE
                    and not locked_self.is_processed
                ):

                    super().save(*args, **kwargs)
                    user = User.objects.select_for_update().get(pk=self.user.pk)
                    user.balance += self.amount
                    user.save(update_fields=["balance"])

                    TransactionHistory.objects.create(
                        seller=user,
                        credit_request=self,
                        amount=self.amount,
                        type=TransactionHistory.TypeChoices.BALANCE_TOP_UP,
                    )

                    # Mark as processed
                    self.is_processed = True
                    super().save(update_fields=["is_processed"])
                else:
                    # If race condition caused re-check to fail, just save normally
                    super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class TransactionHistory(models.Model):
    class TypeChoices(models.TextChoices):
        BALANCE_TOP_UP = "balance_top_up", "افزایش موجودی حساب"
        SIMCARD_CHARGE = "simcard_charge", "شارژ سیم کارت"

    seller = models.ForeignKey(
        User, verbose_name="کاربر فروشنده", on_delete=models.CASCADE, related_name="seller_transactions_history"
    )
    simcard = models.ForeignKey(
        SimCard,
        on_delete=models.SET_NULL,
        verbose_name="شماره سیم کارت",
        related_name="simcard_transactions_history",
        null=True,
        blank=True,
        default=None,
    )
    credit_request = models.OneToOneField(
        CreditRequest,
        on_delete=models.SET_NULL,
        verbose_name="درخواست اعتبار",
        related_name="credit_request_transaction_history",
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
