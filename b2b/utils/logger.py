import logging

simcard_charge_logger = logging.getLogger("simcard_charge_logger")


class SimCardChargeLogger:
    @staticmethod
    def log_start(user_id, amount, simcard_number):
        simcard_charge_logger.info(
            f"[SIMCARD CHARGE START] - User: {user_id} | Amount: {amount} | SimCard: {simcard_number}"
        )

    @staticmethod
    def log_success(user_id, amount, simcard_number, user_balance, simcard_balance, transaction_history_id):
        simcard_charge_logger.info(
            f"[SIMCARD CHARGE SUCCESS] - User: {user_id} | Amount: {amount} | "
            f"SimCard: {simcard_number} | UserBalance: {user_balance} | "
            f"SimCardBalance: {simcard_balance} | TransactionHistoryID: {transaction_history_id}"
        )

    @staticmethod
    def log_validation_error(user_id, amount, simcard_number, error):
        simcard_charge_logger.error(
            f"[SIMCARD CHARGE VALIDATION ERROR] - User: {user_id} | Amount: {amount} | "
            f"SimCard: {simcard_number} | Error: {error}"
        )

    @staticmethod
    def log_system_error(user_id, amount, simcard_number, error):
        simcard_charge_logger.error(
            f"[SIMCARD CHARGE SYSTEM ERROR] - User: {user_id} | Amount: {amount} | "
            f"SimCard: {simcard_number} | Error: {error}"
        )
