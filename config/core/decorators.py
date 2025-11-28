from functools import wraps
from django.http import HttpResponseBadRequest
import logging

logger = logging.getLogger(__name__)

def mode_switch(secure_impl, vulnerable_impl):
    """
    Decorator that dispatches to either a secure or vulnerable view implementation
    depending on the user's current simulation mode (stored in session).

    Args:
        secure_impl (callable): View function for secure mode.
        vulnerable_impl (callable): View function for vulnerable mode.

    Returns:
        callable: A wrapper that delegates to the correct implementation.
    """
    @wraps(secure_impl)
    def _wrapped(request, *args, **kwargs):
        mode = request.session.get("sim_mode", "secure")

        if mode == "vulnerable":
            logger.warning(f"[ModeSwitch] Running VULNERABLE view: {vulnerable_impl.__name__}")
            return vulnerable_impl(request, *args, **kwargs)

        elif mode == "secure":
            logger.info(f"[ModeSwitch] Running SECURE view: {secure_impl.__name__}")
            return secure_impl(request, *args, **kwargs)

        else:
            logger.error(f"[ModeSwitch] Invalid mode value detected: {mode}")
            return HttpResponseBadRequest("Invalid simulation mode.")

    return _wrapped
