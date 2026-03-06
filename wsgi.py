import os
from django.core.wsgi import get_wsgi_application

# Ensure the project directory is in the path if needed
# Use the folder where settings.py is located
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_integrador.settings')

application = get_wsgi_application()
