from django.db import models
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from utils.validators import validate_sim_number


class SimCard(models.Model):
    class OperatorChoices(models.TextChoices):
        MTN = "mtn", "ایرانسل"
        MCI = "mci", "همراه اول"

    number = models.CharField(
        verbose_name=_("mobile number"), max_length=11, unique=True, validators=[validate_sim_number]
    )
    operator = models.CharField(verbose_name=_("mobile number operator"), max_length=3, choices=OperatorChoices.choices)
    balance = models.DecimalField(
        verbose_name=_("simcard charge"), max_digits=12, decimal_places=0, default=Decimal("0"), help_text=_("toman")
    )
    created_at = models.DateTimeField(verbose_name=_("create date"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("update date"), auto_now=True)

    class Meta:
        verbose_name = _("sim card")
        verbose_name_plural = _("sim cards")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.number}"
