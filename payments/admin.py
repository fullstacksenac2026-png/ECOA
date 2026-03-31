from django.contrib import admin
from .models import (
    Payment, GatewayAPI, PaymentTransaction, PaymentCard, 
    PaymentTicket, PaymentPix, PaymentStatus, PaymentReceipt, 
    PaymentError, Refund
)

class PaymentStatusInline(admin.StackedInline):
    model = PaymentStatus
    extra = 0

class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'course', 'amount', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date', 'course')
    search_fields = ('transaction_id', 'user__cpf', 'user__email', 'course__name')
    inlines = [PaymentStatusInline, PaymentTransactionInline]

@admin.register(GatewayAPI)
class GatewayAPIAdmin(admin.ModelAdmin):
    list_display = ('name', 'endpoint_url')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'payment', 'gateway', 'status', 'amount', 'transaction_date')
    list_filter = ('status', 'gateway', 'transaction_date')

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('payment', 'refund_amount', 'refund_date')

admin.site.register(PaymentCard)
admin.site.register(PaymentTicket)
admin.site.register(PaymentPix)
admin.site.register(PaymentStatus)
admin.site.register(PaymentReceipt)
admin.site.register(PaymentError)
