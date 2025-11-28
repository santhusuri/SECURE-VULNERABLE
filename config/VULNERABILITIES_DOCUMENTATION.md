# Vulnerabilities Documentation for the Project

This document describes the 8 vulnerabilities present in the project, where they occur, how an attacker can find or exploit them, and general mitigation advice.

---

## 1. SQL Injection (SQLi)

- **Where it occurs:** Vulnerable product list and product detail pages, vulnerable user input fields such as search or login.
- **Types in this project:**
  - **Error-based SQLi:** Injecting payloads that cause SQL errors revealing database structure.
  - **Union-based SQLi:** Using UNION SELECT to extract data from other tables.
  - **Blind SQLi:** Inferring data by observing application behavior changes.
- **How to find:** An attacker can input SQL syntax in input fields (e.g., `' OR '1'='1' --`) and observe if the application returns unexpected data or errors.
- **How it works:** The application uses raw SQL queries with unsanitized user input, allowing attackers to manipulate the query.
- **Impact:** Data leakage, unauthorized data modification, or deletion.
- **Mitigation:** Use parameterized queries or ORM methods that escape inputs.

---

## 2. Cross-Site Scripting (XSS)

- **Where it occurs:** Vulnerable product search, reviews, or any page rendering user input without proper escaping.
- **Types in this project:**
  - **Stored XSS:** Malicious scripts stored in database and rendered to users (e.g., in reviews).
  - **Reflected XSS:** Scripts reflected in responses from user input (e.g., search queries).
  - **DOM-based XSS:** Client-side scripts manipulating DOM with unsafe data.
- **How to find:** Inject JavaScript payloads like `<script>alert('XSS')</script>` in input fields or URL parameters and check if scripts execute.
- **How it works:** User input is rendered as HTML without sanitization, allowing script injection.
- **Impact:** Session hijacking, defacement, or redirecting users.
- **Mitigation:** Escape or sanitize user inputs before rendering.

---

## 3. Brute Force

- **Where it occurs:** Login pages without rate limiting or account lockout.
- **How to find:** Automated repeated login attempts with different passwords.
- **How it works:** Attackers try many password combinations to gain access.
- **Impact:** Unauthorized account access.
- **Mitigation:** Implement rate limiting, account lockout, and CAPTCHA.

---

## 4. Command Injection

- **Where it occurs:** Backend endpoints that execute system commands with user input.
- **How to find:** Inject shell metacharacters like `; ls` in input fields and observe command execution.
- **How it works:** Unsanitized input is passed to system shell commands.
- **Impact:** Remote code execution.
- **Mitigation:** Avoid shell commands with user input or sanitize inputs strictly.

---

## 5. Malicious File Upload

- **Where it occurs:** File upload features without validation.
- **How to find:** Upload files with dangerous extensions like `.php`, `.exe`.
- **How it works:** Uploaded files can be executed on the server.
- **Impact:** Server compromise.
- **Mitigation:** Validate file types, restrict executable uploads, store files outside web root.

---

## 6. Directory Traversal

- **Where it occurs:** File or resource access endpoints using user-supplied paths.
- **How to find:** Use payloads like `../etc/passwd` to access unauthorized files.
- **How it works:** Unsanitized path input allows access to files outside intended directories.
- **Impact:** Information disclosure.
- **Mitigation:** Normalize and validate file paths, restrict access.

---

## 7. Session Hijacking

- **Where it occurs:** Session management without secure cookies or token validation.
- **How to find:** Capture or guess session tokens like `PHPSESSID=12345`.
- **How it works:** Attackers use stolen session tokens to impersonate users.
- **Impact:** Unauthorized access.
- **Mitigation:** Use secure, HttpOnly cookies, regenerate session IDs, use HTTPS.

---

## 8. CSRF Bypass

- **Where it occurs:** Forms or endpoints without proper CSRF token validation.
- **How to find:** Submit forms with fake or missing CSRF tokens.
- **How it works:** Attackers trick users into submitting unwanted requests.
- **Impact:** Unauthorized actions on behalf of users.
- **Mitigation:** Implement CSRF tokens and validate them on the server.

---

# Summary

This documentation provides an overview of the vulnerabilities in your project, how attackers can find and exploit them, and general mitigation strategies. Use this as a guide to understand the security posture and improve defenses.
