from locust import HttpUser, task, between, constant
import random

user_credentials = [
    {"email": "seller11@yahoo.com", "password": "Aa123321"},
    {"email": "seller12@yahoo.com", "password": "Aa123321"},
    {"email": "seller13@yahoo.com", "password": "Aa123321"},
]

# Moderate Load Test Users=30, Spawn rate=5, wait_time=between(1, 2)
# Heavy Load Test Users=200, Spawn rate=10, wait_time=between(1, 2)
# Spike Test (Hardest) Users=300, Spawn rate=10, wait_time=constant(0)


class SimcardCharger(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        creds = random.choice(user_credentials)

        response = self.client.post("/api/account/auth/token/", json=creds)
        if response.status_code != 200:
            print(f"[ERROR] Login failed for {creds['email']}: {response.text}")
            self.environment.runner.quit()
            return

        token = response.json().get("access")
        if not token:
            print(f"[ERROR] No access token for {creds['email']}")
            self.environment.runner.quit()
            return

        self.client.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json"})

    @task
    def charge_simcard(self):
        payload = {"amount": "1200", "simcard_number": "09170000000"}

        response = self.client.post("/api/simcards/charge/", json=payload)
        if response.status_code != 200:
            print(f"[ERROR] Charge failed: {response.status_code} - {response.text}")
