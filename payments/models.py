from django.db import models

CHOICES_PAYMENT_METHOD = [
    ('card', 'Cartão de Crédito'),
    ('ticket', 'Boleto Bancário'),
    ('pix', 'PIX'), 
]

CHOICES_PAYMENT_STATUS = [
    ('pending', 'Pendente'),
    ('completed', 'Concluído'),
    ('failed', 'Falhou'),
    ('refunded', 'Reembolsado'),
]

# Create your models here.
class Payment(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'Pagamento de {self.amount} para {self.course.name} por {self.user.username}'

class GatewayAPI(models.Model):
    name = models.CharField(max_length=50)
    api_key = models.CharField(max_length=100)
    api_secret = models.CharField(max_length=100)
    endpoint_url = models.URLField()
    def __str__(self):
        return self.name

class PaymentTransaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    gateway = models.ForeignKey(GatewayAPI, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20)  # Ex: 'pending', 'completed', 'failed'
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transação {self.transaction_id} para pagamento de {self.amount} por {self.payment.user.username} via {self.gateway.name}'

class PaymentCard(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='card')
    card_number = models.CharField(max_length=16)
    cardholder_name = models.CharField(max_length=100)
    expiration_date = models.CharField(max_length=5)  # MM/YY
    cvv = models.CharField(max_length=4)

    def __str__(self):
        return f'Cartão {self.card_number[-4:]} para pagamento de {self.payment.amount} por {self.payment.user.username}'
    
class PaymentTicket(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='ticket')
    ticket_number = models.CharField(max_length=100, unique=True)
    due_date = models.DateTimeField()

    def __str__(self):
        return f'Boleto {self.ticket_number} para pagamento de {self.payment.amount} por {self.payment.user.username}'

class PaymentPix(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='pix')
    pix_key = models.CharField(max_length=100, unique=True)
    qr_code = models.ImageField(upload_to='pix_qr_codes/')

    def __str__(self):
        return f'PIX {self.pix_key} para pagamento de {self.payment.amount} por {self.payment.user.username}'

class PaymentStatus(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(max_length=20)  # Ex: 'pending', 'completed', 'failed'
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Status do pagamento de {self.amount} para {self.course.name} por {self.user.username}: {self.status}'

class PaymentReceipt(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=100, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Recibo {self.receipt_number} para pagamento de {self.payment.amount} por {self.payment.user.username}'

class PaymentError(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='errors')
    error_message = models.TextField()
    error_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Erro no pagamento de {self.payment.amount} para {self.payment.course.name} por {self.payment.user.username}: {self.error_message}'

class Refund(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='refund')
    reason = models.TextField()
    refund_date = models.DateTimeField(auto_now_add=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Reembolso de {self.refund_amount} para {self.payment.course.name} por {self.payment.user.username}'