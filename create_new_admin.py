import django
import os
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_integrador.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    cpf = "12345678901"
    email = "admin@example.com"
    password = "adminpassword123"
    
    if User.objects.filter(cpf=cpf).exists():
        print(f"Usuário com CPF {cpf} já existe.")
        return

    user = User.objects.create_superuser(
        cpf=cpf,
        email=email,
        password=password,
        birth_date=date(1990, 1, 1),
        gender='Masculino',
        sexuality='Heterossexual'
    )
    print(f"Superusuário criado com sucesso!")
    print(f"CPF: {cpf}")
    print(f"Email: {email}")

if __name__ == "__main__":
    create_admin()
