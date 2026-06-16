SUPER_TYPES = {'Super Admin', 'MD'}
PRIVILEGED = {'Super Admin', 'Admin', 'MD'}


def roles(request):
    """Expose is_super / is_privileged / user_type / region to every template."""
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {'is_super': False, 'is_privileged': False, 'user_type': None, 'my_region': ''}
    emp = getattr(user, 'employee', None)
    user_type = emp.user_type if emp else ('Super Admin' if user.is_superuser else None)
    is_super = user.is_superuser or (emp is not None and emp.user_type in SUPER_TYPES)
    is_privileged = user.is_superuser or (emp is not None and emp.user_type in PRIVILEGED)
    return {
        'is_super': is_super,
        'is_privileged': is_privileged,
        'user_type': user_type,
        'my_region': emp.region if emp else '',
    }
