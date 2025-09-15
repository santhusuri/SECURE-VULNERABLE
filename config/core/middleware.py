#core/middleware
from django.utils.deprecation import MiddlewareMixin
from .logger import send_security_event, write_ids_log
import re

class SimulationSecurityMiddleware(MiddlewareMixin):
    SQLI_PATTERNS = [
        r"('|\").*or.*=.*",  
        r"union\s+select",   
        r"drop\s+table",     
        r"--"                
    ]
    XSS_PATTERNS = [
        r"<script.*?>",      
        r"onerror\s*=",      
        r"alert\s*\("        
    ]
    BRUTEFORCE_PATTERNS = [
        r"failed login",
        r"invalid password"
    ]

    def process_request(self, request):
        """
        Capture POST requests and log them to both secure and vulnerable logs.
        Forward suspicious activity to Project B.
        """
        if request.method == "POST":
            user_ip = request.META.get("REMOTE_ADDR", "unknown")
            try:
                data = request.POST.dict()
                # Mask password fields
                masked_data = {k: ("*****" if "password" in k.lower() else v) for k, v in data.items()}
                event_msg = f"POST to {request.path}: {masked_data}"

                # Determine mode (session key or default to 'secure')
                mode = request.session.get("sim_mode", "secure")

                # Write IDS log for both modes
                write_ids_log(user_id=user_ip, action=f"[{mode.upper()} MODE] {event_msg}")

                # Detect attack type
                attack_type = None
                lowered = str(masked_data).lower()

                if any(re.search(p, lowered) for p in self.SQLI_PATTERNS):
                    attack_type = "sql_injection"
                elif any(re.search(p, lowered) for p in self.XSS_PATTERNS):
                    attack_type = "xss"
                elif any(re.search(p, lowered) for p in self.BRUTEFORCE_PATTERNS):
                    attack_type = "bruteforce"

                # Send suspicious events to Project B only
                if attack_type:
                    send_security_event(f"{attack_type} detected in {mode} mode: {event_msg}", user_ip)

            except Exception as e:
                print(f"[Middleware] Failed to log/send event: {e}")
        return None

    def process_response(self, request, response):
        """
        Set response headers based on secure/vulnerable mode.
        """
        mode = request.session.get('sim_mode', 'secure')

        if mode == 'secure':
            response.headers.setdefault('X-Content-Type-Options', 'nosniff')
            response.headers.setdefault('X-Frame-Options', 'DENY')
            response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
            response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=()')
        else:
            response.headers.pop('X-Frame-Options', None)

        return response
