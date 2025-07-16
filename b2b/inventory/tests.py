from django.urls import reverse
from django.test import TransactionTestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from inventory.models import SimCard
from finance.models import CreditRequest, TransactionHistory
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from django.db import models, connection
import random


User = get_user_model()


class CreditRequestAndSimcardChargeFlowTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="seller111@test.com", password="pass123")
        self.user2 = User.objects.create_user(email="seller222@test.com", password="pass123")

        self.simcards = []
        for i in range(5):
            sim = SimCard.objects.create(number=f"0912000000{i}", operator="mci")
            self.simcards.append(sim)

    def test_credit_and_charge_flow(self):
        for user in [self.user1, self.user2]:
            self.client.force_authenticate(user=user)
            for _ in range(10):
                response = self.client.post(
                    reverse("finance:credit-requests-create"),
                    data={"amount": 500000 if user == self.user1 else 200000},
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        credit_requests = CreditRequest.objects.all()
        for req in credit_requests:
            req.status = CreditRequest.StatusChoices.COMPLETE
            req.save()

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        print(f"User: {self.user1.email} initial balance = {self.user1.balance}")
        print(f"User: {self.user2.email} initial balance = {self.user2.balance}")

        for user in [self.user1, self.user2]:
            self.client.force_authenticate(user=user)
            success_count = 0
            for i in range(1000):
                sim_number = random.choice(self.simcards).number
                response = self.client.post(
                    reverse("inventory:simcard-charge"),
                    data={"amount": 3000, "simcard_number": sim_number},
                    format="json",
                )
                if user == self.user1:
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    success_count += 1
                else:
                    if response.status_code == status.HTTP_200_OK:
                        success_count += 1
                    elif response.status_code == status.HTTP_400_BAD_REQUEST:
                        self.assertIn("amount", response.json())

            print(f"User: {user.email} succeeded in {success_count}/1000 charges.")

        for user in [self.user1, self.user2]:
            top_ups = TransactionHistory.objects.filter(
                seller=user, type=TransactionHistory.TypeChoices.BALANCE_TOP_UP
            ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

            charges = TransactionHistory.objects.filter(
                seller=user, type=TransactionHistory.TypeChoices.SIMCARD_CHARGE
            ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

            expected_balance = top_ups - charges

            print(f"User: {user.email} transaction history total top-ups = {top_ups}, total charges = {charges}")

            user.refresh_from_db()

            print(f"User: {user.email} final balance = {user.balance}")

            self.assertEqual(user.balance, expected_balance)


class ConcurrentSimcardChargeTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="seller@test.com", password="pass123")
        self.simcard = SimCard.objects.create(number="09190000001", operator="mci")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("finance:credit-requests-create"),
            data={"amount": 7000000},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

        self.credit_request = CreditRequest.objects.get(user=self.user, status=CreditRequest.StatusChoices.PENDING)
        self.credit_request.status = CreditRequest.StatusChoices.COMPLETE
        self.credit_request.save()

        self.user.refresh_from_db()

    def _make_charge_request(self):
        try:
            client = APIClient()
            client.force_authenticate(user=self.user)

            response = client.post(
                reverse("inventory:simcard-charge"),
                data={"amount": 3000, "simcard_number": self.simcard.number},
                format="json",
            )

            assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
        finally:
            # this will prevent test database destroy error due to workers count opened sessions
            connection.close()

    def test_concurrent_simcard_charges(self):
        total_requests = 2000
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(self._make_charge_request) for _ in range(total_requests)]
            for future in as_completed(futures):
                future.result()  # Will raise if any thread had an assertion failure

        top_ups = TransactionHistory.objects.filter(
            seller=self.user, type=TransactionHistory.TypeChoices.BALANCE_TOP_UP
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

        charges = TransactionHistory.objects.filter(
            seller=self.user, type=TransactionHistory.TypeChoices.SIMCARD_CHARGE
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

        self.user.refresh_from_db()
        self.simcard.refresh_from_db()

        print(f"User balance: {self.user.balance}")
        print(f"Total top-ups: {top_ups}")
        print(f"Total charges: {charges}")
        print(f"Simcard balance: {self.simcard.balance}")

        self.assertEqual(self.user.balance, top_ups - charges)
        self.assertEqual(self.simcard.balance, charges)
