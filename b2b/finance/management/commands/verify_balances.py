from django.core.management.base import BaseCommand
from django.db.models import Sum, Q
from django.contrib.auth import get_user_model
from inventory.models import SimCard
from finance.models import TransactionHistory

User = get_user_model()


class Command(BaseCommand):
    help = "Verify simcard balances and user balances against transaction history"

    def handle(self, *args, **options):
        errors = []

        print("\n🔍 Checking all simcards...")
        for simcard in SimCard.objects.all():
            total_charge = (
                TransactionHistory.objects.filter(
                    simcard=simcard, type=TransactionHistory.TypeChoices.SIMCARD_CHARGE
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            )

            if simcard.balance != total_charge:
                errors.append(
                    f"[SIMCARD ERROR] SimCard {simcard.number} balance mismatch: balance={simcard.balance} vs total_charge={total_charge}"
                )

        print("\n🔍 Checking all users...")
        for user in User.objects.all():
            total_top_up = (
                TransactionHistory.objects.filter(
                    seller=user, type=TransactionHistory.TypeChoices.BALANCE_TOP_UP
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            )

            total_charges = (
                TransactionHistory.objects.filter(
                    seller=user, type=TransactionHistory.TypeChoices.SIMCARD_CHARGE
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            )

            expected_balance = total_top_up - total_charges

            if user.balance != expected_balance:
                errors.append(
                    f"[USER ERROR] User {user.pk} balance mismatch: balance={user.balance} vs expected={expected_balance} (top_up={total_top_up}, charges={total_charges})"
                )

        if errors:
            print("\n❌ Validation completed with errors:")
            for err in errors:
                print(err)
        else:
            print("\n✅ All balances are consistent.")
