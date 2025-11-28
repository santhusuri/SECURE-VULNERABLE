# core/context_processors.py
from django.conf import settings

def simulation_mode(request):
    """
    Inject 'simulation_mode' into all templates.
    - Primary source: request.session['sim_mode']
    - Fallback: settings.SIMULATION_MODE (default in settings.py)
    """
    session_mode = request.session.get(
        "sim_mode", getattr(settings, "SIMULATION_MODE", "secure")
    )
    return {"simulation_mode": session_mode}
