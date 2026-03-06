from notifications.models import Notification

def notifications(request):
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]  # Limit to 10 recent
        return {'notifications': user_notifications}
    return {'notifications': []}