from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

TYPE_MESSAGE_CHOICES = [
    ('ERROR', 'ERROR'),
    ('WARNING', 'WARNING'),
    ('SUCCESS', 'SUCCESS'),
]

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    type_message = models.CharField(max_length=10, choices=TYPE_MESSAGE_CHOICES)
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now=True)