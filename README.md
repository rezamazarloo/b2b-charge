# Django Project – B2B Recharge and Credit Management System

This Django-based backend system is a demo project which is designed to support a **B2B mobile recharge service** where multiple sellers can request and manage account credits and sell mobile recharge to customers. The platform ensures accurate financial accounting, reliable transaction processing, and resistance to race conditions or data corruption.

---

## 📘 Project Overview

The system supports the following workflow:

- Multiple sellers are registered in the system.
- Each seller has a credit balance (in Tomans).
- Sellers can:
  - Request a credit increase via a designated API endpoint.
  - Recharge phone numbers via a POST API call.
- For each recharge:
  - The system checks if the seller has enough credit.
  - Deducts the correct amount from their balance.
  - Logs the transaction in detail.
- Credit and accounting data are always kept in sync with transactional records.

---

## ✅ Key Functional Requirements

1. **Seller Credit Management**
   - Credit can only be increased through a controlled API.
   - Sellers cannot have a negative credit balance.

2. **Recharge Transactions**
   - Sellers submit recharge requests for specific phone numbers.
   - The request includes the recharge amount.
   - The system processes the request only if the seller has enough credit.
   - Recharge logs are created and stored.
   - The deducted amount must match the recharge amount exactly.

3. **Financial Consistency**
   - The backend accounting system must match recharge records precisely.
   - Example:
     > If a seller was credited with 1,000,000 Tomans and sold 60 recharges of 5,000 Tomans each, their remaining balance must be exactly 700,000 Tomans.

4. **Data Integrity & Safety**
   - The system must prevent:
     - Race conditions.
     - Double spending.
     - Inconsistent credit changes.
   - All updates must be **atomic** and reliable under high concurrency.

---

## 🔬 Testing Requirements

- Must include a test case involving:
  - At least 10 sellers.
  - 1000 recharge transactions.
- Validate the final balance of each seller matches expected outcomes.
- Load testing under high concurrency to simulate real-world demand.
- Ensure safe operation under multithreaded and multiprocess environments.
