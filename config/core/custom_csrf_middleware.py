from django.middleware.csrf import CsrfViewMiddleware

class CustomCsrfMiddleware(CsrfViewMiddleware):
    def _reject(self, request, reason):
        mode = request.session.get("sim_mode", "secure")
        if mode == "vulnerable":
            return None  # Skip CSRF check in vulnerable mode
        return super()._reject(request, reason)
