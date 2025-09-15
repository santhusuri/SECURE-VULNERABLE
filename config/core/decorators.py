from functools import wraps
from django.http import HttpResponseBadRequest

def mode_switch(secure_impl, vulnerable_impl):
    """
    Decorator to switch between secure and vulnerable implementations of a view
    based on the 'sim_mode' value stored in the user's session.

    Args:
        secure_impl (callable): The view function for secure mode.
        vulnerable_impl (callable): The view function for vulnerable mode.

    Returns:
        callable: A wrapped view dispatching to the appropriate implementation.
    """
    @wraps(secure_impl)
    def _wrapped(request, *args, **kwargs):
        mode = request.session.get('sim_mode', 'secure')
        if mode == 'vulnerable':
            return vulnerable_impl(request, *args, **kwargs)
        elif mode == 'secure':
            return secure_impl(request, *args, **kwargs)
        else:
            # Optional: handle unexpected mode values gracefully
            return HttpResponseBadRequest("Invalid simulation mode.")
    return _wrapped
