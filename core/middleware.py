from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

class UserSecurityMiddleware(MiddlewareMixin):
    """
    Middleware para capturar IP e impedir que usuários bloqueados acessem o sistema.
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            # 1. Bloqueio de Usuário
            if getattr(request.user, 'is_blocked', False):
                messages.error(request, "Sua conta está bloqueada pelo administrador.")
                logout(request)
                return redirect('authorization:login')
            
            # 2. Captura de IP
            ip = self.get_client_ip(request)
            if request.user.last_ip != ip:
                request.user.last_ip = ip
                request.user.save(update_fields=['last_ip'])

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
