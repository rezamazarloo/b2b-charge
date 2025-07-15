from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_sim_number(value):
    """
    Validate that the SIM number starts with 09 and is exactly 11 characters long.
    """
    if not value.startswith("09"):
        raise ValidationError(_("SIM number must start with '09'."))

    if len(value) != 11:
        raise ValidationError(_("SIM number must be exactly 11 characters long."))

    if not value.isdigit():
        raise ValidationError(_("SIM number must contain only digits."))
