from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from inventory.models import SimCard
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = "Populate test users and simcards"

    def handle(self, *args, **options):
        password = "Aa123321"

        # Create superuser
        if not User.objects.filter(email="rezamazarloo@yahoo.com").exists():
            User.objects.create_superuser(
                email="rezamazarloo@yahoo.com",
                password=password,
                first_name="رضا",
                last_name="مزارلو",
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS("Superuser created."))

        # Create 5 seller users
        for i in range(10, 16):
            email = f"seller{i}@yahoo.com"
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email, password=password, first_name=f"Seller", last_name=i, is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f"Created user {email}"))

        # Create 9 simcards
        sim_numbers = [
            "09110000000",
            "09120000000",
            "09130000000",
            "09140000000",
            "09150000000",
            "09160000000",
            "09170000000",
            "09180000000",
            "09190000000",
        ]

        for num in sim_numbers:
            if not SimCard.objects.filter(number=num).exists():
                operator = "mci" if num.startswith("091") else "mtn"
                SimCard.objects.create(number=num, operator=operator)
                self.stdout.write(self.style.SUCCESS(f"Created simcard {num}"))
