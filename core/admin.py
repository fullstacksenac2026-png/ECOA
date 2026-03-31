from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from authorization.models import User
from pictures.models import Picture, Complaint

# Customizando o site administrativo padrão
admin.site.site_header = _("Painel de Comando ECOA")
admin.site.site_title = _("ECOA Administrativo")
admin.site.index_title = _("Bem-vindo ao Gerenciamento ECOA")

# Sobrescrever o método index do Admin padrão para injetar estatísticas
original_index = admin.site.index

def ecoa_index(request, extra_context=None):
    # 1. Estatísticas para o Dashboard
    active_users_count = User.objects.filter(is_active=True, is_blocked=False).count()
    blocked_users_count = User.objects.filter(is_blocked=True).count()
    total_pictures = Picture.objects.count()
    
    # Tentativa segura de contar denúncias
    try:
        pending_complaints = Complaint.objects.count()
    except:
        pending_complaints = 0

    extra_context = extra_context or {}
    extra_context.update({
        'active_users_count': active_users_count,
        'blocked_users_count': blocked_users_count,
        'total_pictures': total_pictures,
        'pending_complaints': pending_complaints,
    })
    return original_index(request, extra_context)

# Aplicar o patch
admin.site.index = ecoa_index
