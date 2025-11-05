from .models import AcademicSession, AcademicTerm, SiteConfig


def site_defaults(request):
    # Safely get current session
    try:
        current_session = AcademicSession.objects.get(current=True)
        current_session_name = current_session.name
    except AcademicSession.DoesNotExist:
        current_session_name = "No Session Set"

    # Safely get current term
    try:
        current_term = AcademicTerm.objects.get(current=True)
        current_term_name = current_term.name
    except AcademicTerm.DoesNotExist:
        current_term_name = "No Term Set"

    vals = SiteConfig.objects.all()
    contexts = {
        "current_session": current_session_name,
        "current_term": current_term_name,
    }
    for val in vals:
        contexts[val.key] = val.value

    return contexts