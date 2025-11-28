# core/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .logger import send_security_event, write_ids_log, write_airs_log
import re
import logging

logger = logging.getLogger(__name__)

class SimulationSecurityMiddleware(MiddlewareMixin):
    """
    Middleware to:
    - Monitor incoming requests for common attack patterns
    - Log events in IDS / AIRS
    - Send suspicious activity to external security service (Project B)
    - Apply security headers in secure mode, relax them in vulnerable mode

    NOTE: This is a lab/demo middleware. In production you would not intentionally
    weaken security or log raw request contents.
    """

    # Raw string patterns (kept as readable list)
    SQLI_PATTERNS = [
        r"('|\").*or.*=.*",
        r"union\s+select",
        r"drop\s+table",
        r"--",
        r"sleep\([0-9]+\)",
    ]

    XSS_PATTERNS = [
        r"<script.*?>",
        r"onerror\s*=",
        r"alert\s*\(",
        r"javascript:",
        r"<img.*src=.*>",
    ]

    BRUTEFORCE_PATTERNS = [
        r"failed login",
        r"invalid password",
        r"too many attempts",
    ]

    CMDI_PATTERNS = [
        r";\s*ls",
        r";\s*cat",
        r"&\s*whoami",
        r"\|\s*nc",
    ]

    FILEUPLOAD_PATTERNS = [
        r"\.php$", r"\.exe$", r"\.jsp$", r"\.asp$",
    ]

    DIR_TRAVERSAL_PATTERNS = [
        r"\.\./", r"\.\.\\", r"etc/passwd", r"boot.ini",
    ]

    SESSION_PATTERNS = [
        r"PHPSESSID", r"JSESSIONID", r"token=.*\.\.",
    ]

    CSRF_PATTERNS = [
        r"csrfmiddlewaretoken=", r"forged_csrf", r"fake_token",
    ]

    # Compile regexes once for performance (case-insensitive)
    _compiled_groups = None

    @classmethod
    def _compile_patterns(cls):
        if cls._compiled_groups is None:
            cls._compiled_groups = {
                "sqli": [re.compile(p, re.IGNORECASE) for p in cls.SQLI_PATTERNS],
                "xss": [re.compile(p, re.IGNORECASE) for p in cls.XSS_PATTERNS],
                "bruteforce": [re.compile(p, re.IGNORECASE) for p in cls.BRUTEFORCE_PATTERNS],
                "cmdi": [re.compile(p, re.IGNORECASE) for p in cls.CMDI_PATTERNS],
                "fileupload": [re.compile(p, re.IGNORECASE) for p in cls.FILEUPLOAD_PATTERNS],
                "dir_traversal": [re.compile(p, re.IGNORECASE) for p in cls.DIR_TRAVERSAL_PATTERNS],
                "session": [re.compile(p, re.IGNORECASE) for p in cls.SESSION_PATTERNS],
                "csrf": [re.compile(p, re.IGNORECASE) for p in cls.CSRF_PATTERNS],
            }
        return cls._compiled_groups

    def process_request(self, request):
        """
        Inspect POST requests and detect suspicious patterns.
        """

        # Only inspect POSTs to limit noise and cost
        if request.method != "POST":
            return None

        # Basic client identification
        user_ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "unknown")).split(",")[0].strip()

        try:
            # Try to get POST data safely; if not form-encoded, fall back to raw body (limited size)
            try:
                data_dict = request.POST.dict()
            except Exception:
                # request.POST may be empty for non-form payloads; read raw body but cap length
                raw = request.body[:4096] if request.body else b""
                try:
                    data_dict = {"_raw_body": raw.decode("utf-8", errors="ignore")}
                except Exception:
                    data_dict = {"_raw_body": str(raw)}

            # Mask obvious sensitive keys to avoid logging secrets
            masked_data = {
                k: ("*****" if "password" in k.lower() or "token" in k.lower() else v)
                for k, v in data_dict.items()
            }

            # Build event message (short)
            event_msg = f"POST to {request.path}: {masked_data}"

            # Determine simulation mode (uses sim_mode for compatibility with your sessions)
            mode = request.session.get("sim_mode", "secure")

            # Write IDS log (simple)
            write_ids_log(user_id=user_ip, action=f"[{mode.upper()} MODE] {event_msg}")

            # Flatten masked data for scanning (limit to first N chars to avoid huge regex scans)
            scan_text = str(masked_data).lower()[:8000]  # cap length

            # Compile patterns if needed
            groups = self._compile_patterns()

            attack_type = None
            if any(p.search(scan_text) for p in groups["sqli"]):
                attack_type = "sql_injection"
            elif any(p.search(scan_text) for p in groups["xss"]):
                attack_type = "xss"
            elif any(p.search(scan_text) for p in groups["bruteforce"]):
                attack_type = "bruteforce"
            elif any(p.search(scan_text) for p in groups["cmdi"]):
                attack_type = "command_injection"
            elif any(p.search(scan_text) for p in groups["fileupload"]):
                attack_type = "malicious_file_upload"
            elif any(p.search(scan_text) for p in groups["dir_traversal"]):
                attack_type = "directory_traversal"
            elif any(p.search(scan_text) for p in groups["session"]):
                attack_type = "session_hijacking"
            elif any(p.search(scan_text) for p in groups["csrf"]):
                attack_type = "csrf_bypass"

            if attack_type:
                msg = f"{attack_type} detected in {mode} mode: {event_msg}"
                # AIRS log + external event
                try:
                    write_airs_log(attack_type)
                except Exception:
                    logger.exception("Failed to write AIRS log")

                try:
                    send_security_event(msg, user_ip)
                except Exception:
                    logger.exception("Failed to send security event")

        except Exception:
            logger.exception("[Middleware] Unexpected error while scanning request")

        return None

    def process_response(self, request, response):
        """
        Apply or relax security headers depending on mode.
        """
        mode = request.session.get("sim_mode", "secure")

        if mode == "secure":
            # set headers if missing
            response.headers.setdefault("X-Content-Type-Options", "nosniff")
            response.headers.setdefault("X-Frame-Options", "DENY")
            response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
            response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=()")
        else:
            # Vulnerable mode: intentionally weaken headers (lab only)
            response.headers.pop("X-Frame-Options", None)
            # you might explicitly remove other headers here for demo purposes

        return response
