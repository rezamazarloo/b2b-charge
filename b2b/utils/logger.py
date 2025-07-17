import logging
from django.urls import reverse_lazy

simcard_charge_logger = logging.getLogger("simcard_charge_logger")


class SimCardChargeLogger:
    ENDPOINT = reverse_lazy("inventory:simcard-charge")

    @classmethod
    def log_start(cls, user_id, amount, simcard_number):
        simcard_charge_logger.info(
            f"{cls.ENDPOINT} | [SIMCARD CHARGE START] - User: {user_id} | Amount: {amount} | SimCard: {simcard_number}"
        )

    @classmethod
    def log_success(cls, user_id, amount, simcard_number, user_balance, simcard_balance, transaction_history_id):
        simcard_charge_logger.info(
            f"{cls.ENDPOINT} | [SIMCARD CHARGE SUCCESS] - User: {user_id} | Amount: {amount} | "
            f"SimCard: {simcard_number} | UserBalance: {user_balance} | "
            f"SimCardBalance: {simcard_balance} | TransactionHistoryID: {transaction_history_id}"
        )

    @classmethod
    def log_validation_error(cls, user_id, amount, simcard_number, error):
        simcard_charge_logger.error(
            f"{cls.ENDPOINT} | [SIMCARD CHARGE VALIDATION ERROR] - User: {user_id} | Amount: {amount} | "
            f"SimCard: {simcard_number} | Error: {error}"
        )

    @classmethod
    def log_system_error(cls, user_id, amount, simcard_number, error):
        simcard_charge_logger.error(
            f"{cls.ENDPOINT} | [SIMCARD CHARGE SYSTEM ERROR] - User: {user_id} | Amount: {amount} | "
            f"SimCard: {simcard_number} | Error: {error}"
        )
