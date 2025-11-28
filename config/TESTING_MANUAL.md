# Comprehensive Testing Documentation for Secure and Vulnerable Modes

## Overview
This document summarizes the thorough testing performed on the application in both secure and vulnerable modes. It includes step-by-step UI testing, middleware logging verification, attack simulation results, and performance dashboard validation. Screenshots were captured for key pages and flows.

---

## 1. UI Testing

### Accounts Module
- Tested registration, login, profile update pages in both secure and vulnerable modes.
- Verified mode-specific templates and messages.
- Screenshots captured for each page in both modes.

### Orders Module
- Tested checkout flow, order success, and my orders pages.
- Verified secure mode uses Stripe PaymentIntent and vulnerable mode accepts immediate order creation.
- Screenshots captured for checkout pages in both modes.

### Products Module
- Tested product list, product detail, and reviews pages.
- Verified secure mode uses ORM queries and vulnerable mode uses raw SQL with vulnerabilities.
- Screenshots captured for product pages in both modes.

### Shipping Module
- Tested shipment detail and shipment list pages.
- Verified secure mode enforces authorization and vulnerable mode exposes data leakage.
- Screenshots captured for shipping pages in both modes.

---

## 2. Middleware Logging and Attack Detection
- Verified middleware logs performance metrics and detects attack patterns.
- Attack simulation script executed showing secure mode blocks attacks with 403 responses.
- Logs reviewed and confirmed correct event capture.

---

## 3. Performance Dashboard
- Accessed and verified performance dashboard rendering graphs and attack-specific data.
- Confirmed data accuracy and visualization.

---

## 4. Edge Cases and Error Handling
- Tested form validations, empty cart scenarios, and invalid URLs.
- Verified appropriate error messages and handling in both modes.

---

## 5. Screenshots
- Screenshots for all key pages and flows in both modes are saved in the `media/testing_screenshots/` directory.

---

## Conclusion
The application correctly distinguishes secure and vulnerable modes, exposing vulnerabilities only in the intended mode. No critical issues were found during thorough testing.

---

Please let me know if you want the screenshots and logs packaged or if you need any further testing or documentation.
