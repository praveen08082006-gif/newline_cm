PRIVILEGED = {'Super Admin', 'Admin', 'MD'}


def roles(request):
    """Expose is_privileged + user_type to every template (for sidebar menu)."""
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {'is_privileged': False, 'user_type': None}
    emp = getattr(user, 'employee', None)
    user_type = emp.user_type if emp else ('Super Admin' if user.is_superuser else None)
    is_privileged = user.is_superuser or (emp is not None and emp.user_type in PRIVILEGED)
    return {'is_privileged': is_privileged, 'user_type': user_type}
