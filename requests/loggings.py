from .models import RequestLog

def log_request_action(request_obj, user, action, message=None):
    """
    Helper to create a RequestLog entry.
    """
    return RequestLog.objects.create(
        request=request_obj,
        user=user,
        action=action,
        message=message or ''
    ).save()
