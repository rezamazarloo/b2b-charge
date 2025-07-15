from django.core.exceptions import ValidationError


def validate_sim_number(value):
    """
    Validate that the SIM number starts with 09 and is exactly 11 characters long.
    """
    if not value.startswith("09"):
        raise ValidationError("شماره سیم کارت باید با 09 شروع شود.")

    if len(value) != 11:
        raise ValidationError("شماره سیم کارت باید 11 رقم باشد.")

    if not value.isdigit():
        raise ValidationError("شماره سیم کارت باید فقط شامل اعداد باشد.")
