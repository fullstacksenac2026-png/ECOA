from django.test import TestCase, Client
from django.urls import reverse
from authorization.models import User
from .models import Course, Enrollment
import os

# Create your tests here.

class PurchaseFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(cpf='12345678901', email='test@example.com', password='pass1234', birth_date='2000-01-01', gender='Masculino', sexuality='Heterossexual')
        self.course_free = Course.objects.create(name='Free', description='free', price=0, time='1h')
        self.course_paid = Course.objects.create(name='Paid', description='paid', price=50.0, time='2h')
        os.environ['MERCADO_PAGO_PUBLIC_KEY'] = 'PUBLIC_KEY'
        os.environ['MERCADO_PAGO_ACCESS_TOKEN'] = 'ACCESS_TOKEN'

    def test_free_course_enroll(self):
        self.client.login(cpf='12345678901', password='pass1234')
        url = reverse('courses:course-checkout', args=[self.course_free.id])
        response = self.client.get(url)
        # free course should redirect to lessons immediately
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(course=self.course_free, user=self.user).exists())

    def test_paid_course_checkout_page(self):
        self.client.login(cpf='12345678901', password='pass1234')
        url = reverse('courses:course-checkout', args=[self.course_paid.id])
        # monkeypatch mercadopago to avoid network calls
        class DummyPreference:
            def __init__(self):
                self.response = {'id': 'pref_123'}
        class DummySDK:
            def __init__(self, token):
                pass
            def preference(self):
                return self
            def create(self, data):
                return {'response': {'id': 'pref_123'}}
        import mercadopago
        mercadopago.SDK = DummySDK
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pref_123')
        self.assertContains(response, 'PUBLIC_KEY')
