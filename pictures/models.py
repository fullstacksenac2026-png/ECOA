from django.db import models
from authorization.models import User
TITLE_COMPLAINT_CHOICES = [
    ('POLUICAO_TERRESTRE', 'Poluição terrestre'),
    ('POLUICAO_AEREA', 'Poluição Aérea'),
    ('POLUICAO_AQUATICA', 'Poluição Aquática'),
    ('POLUICAO_PUBLICA', 'Poluição em ambiente público'),
    ('POLUICAO_PUBLICA_PRIVADA', 'Poluição em ambiente público e privado'),
    ('POLUICAO_PRIVADA', 'Poluição em ambiente privado'),
]

# Create your models here.
class Picture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pictures')

    image = models.ImageField(upload_to='picture_images')
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Complaint(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name='complaints')

    title = models.CharField(max_length=255, choices=TITLE_COMPLAINT_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Geolocation(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name='geolocations')

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

class Verify(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, related_name='verifies')

    is_fake = models.BooleanField()
    verify_message = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
