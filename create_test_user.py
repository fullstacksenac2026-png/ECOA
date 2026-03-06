import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_integrador.settings')
django.setup()

from authorization.models import User

# Check if user already exists
if not User.objects.filter(cpf='12345678901').exists():
    user = User(
        cpf='12345678901',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        birth_date=datetime.date(1990, 1, 1),
        gender='Masculino',
        sexuality='Heterossexual',
        is_staff=True,
        is_superuser=True
    )
    user.set_password('admin')
    user.save()
    print("Superuser created: CPF=12345678901, Password=admin")
else:
    print("Superuser already exists.")
