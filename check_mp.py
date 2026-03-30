import os, sys, django
sys.path.append(r'c:\Users\LABTEMP-01\Documents\Full Stack\Leon\Django\Senac\projeto_integrador (2)\projeto_integrador\projeto_integrador\projeto_integrador')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_integrador.settings')
django.setup()
from django.conf import settings
import mercadopago
sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
preference_data = {
    'items': [{'title': 'Test', 'quantity': 1, 'unit_price': 100.0, 'currency_id': 'BRL'}],
    'back_urls': {
        'success': 'http://127.0.0.1:8000/courses/payment/success/',
        'failure': 'http://127.0.0.1:8000/courses/payment/failure/',
        'pending': 'http://127.0.0.1:8000/courses/payment/pending/'
    }
}

print('127.0.0.1 without auto_return =>', sdk.preference().create(preference_data).get('status', 'no_status'))
