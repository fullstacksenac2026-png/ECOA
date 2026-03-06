from enum import unique
from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
GENDER_CHOICES = [
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino'),
    ('Outro', 'Outro'),
    ('Prefiro não dizer', 'Prefiro não dizer'),
]

SEXUALITY_CHOICES = [
    ('Heterossexual', 'Heterossexual'),
    ('Homossexual', 'Homossexual'),
    ('Bissexual', 'Bissexual'),
    ('Assexual', 'Assexual'),
    ('Outro', 'Outro'),
    ('Prefiro não dizer', 'Prefiro não dizer'),
]



class User(AbstractUser):
    username = None
    email = models.EmailField()
    cpf = models.CharField(max_length=14, unique=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    sexuality = models.CharField(max_length=20, choices=SEXUALITY_CHOICES)

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = []

class Phone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phones')

    ddi = models.CharField(max_length=5)
    ddd = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    is_mobile = models.BooleanField(default=False)

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')

    cep = models.CharField(max_length=9)
    residence_number = models.CharField(max_length=10)
    complement = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

