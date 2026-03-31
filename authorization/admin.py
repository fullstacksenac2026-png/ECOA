from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Phone, Address

class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1

class AddressInline(admin.StackedInline):
    model = Address
    extra = 1

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Definir campos exibidos na listagem
    list_display = ('cpf', 'email', 'first_name', 'last_name', 'is_blocked', 'last_ip', 'is_staff')
    # Campos de busca
    search_fields = ('cpf', 'email', 'first_name', 'last_name', 'last_ip')
    # Filtros laterais
    list_filter = ('is_blocked', 'is_staff', 'is_superuser', 'is_active', 'gender')
    # Ordenação padrão
    ordering = ('cpf',)
    
    actions = ['block_users', 'unblock_users']

    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)
        self.message_user(request, "Usuários selecionados foram bloqueados.")
    block_users.short_description = "Bloquear usuários selecionados"

    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)
        self.message_user(request, "Usuários selecionados foram desbloqueados.")
    unblock_users.short_description = "Desbloquear usuários selecionados"

    # Username_field nesse projeto é o CPF
    fieldsets = (
        (None, {'fields': ('cpf', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email', 'birth_date', 'gender', 'sexuality', 'profile_picture')}),
        ('Segurança e Acesso', {'fields': ('is_blocked', 'last_ip', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('cpf', 'email', 'first_name', 'last_name', 'birth_date', 'gender', 'sexuality', 'password'),
        }),
    )
    
    inlines = [PhoneInline, AddressInline]

@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('user', 'ddd', 'phone_number', 'is_mobile')
    search_fields = ('user__cpf', 'phone_number')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'cep')
    search_fields = ('user__cpf', 'cep', 'city')
