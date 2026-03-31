from enum import unique
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from datetime import date

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

class UserManager(BaseUserManager):
    def create_user(self, cpf, password=None, **extra_fields):
        if not cpf:
            raise ValueError('CPF é obrigatório.')
        
        # Valores padrão para evitar erro de banco de dados
        if 'email' not in extra_fields:
            extra_fields['email'] = ''
        if 'birth_date' not in extra_fields:
            extra_fields['birth_date'] = date(2000, 1, 1)
        if 'gender' not in extra_fields:
            extra_fields['gender'] = 'Prefiro não dizer'
        if 'sexuality' not in extra_fields:
            extra_fields['sexuality'] = 'Prefiro não dizer'

        user = self.model(cpf=cpf, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(cpf, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    sexuality = models.CharField(max_length=20, choices=SEXUALITY_CHOICES, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Novos campos de segurança
    is_blocked = models.BooleanField(default=False, verbose_name="Está Bloqueado?")
    last_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Último IP de Acesso")

    objects = UserManager()

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

