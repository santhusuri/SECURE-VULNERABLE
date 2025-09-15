#core/content_processors
from django.conf import settings

def simulation_mode(request):
    """
    Add the current simulation mode to template context.
    Defaults to settings.SIMULATION_MODE if session key missing.
    """
    mode = request.session.get('sim_mode')
    if not mode:
        # Use project default from settings
        mode = getattr(settings, "SIMULATION_MODE", "secure")
        request.session['sim_mode'] = mode

    return {"simulation_mode": mode}  # consistent with JS base.html



