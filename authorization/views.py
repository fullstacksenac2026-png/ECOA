from django.shortcuts import render
import re
from django.http import JsonResponse
from django.urls import reverse
from .forms import UserLoginForm, UserRegisterForm, PhoneRegisterForm, AddressRegisterForm, PasswordResetForm, UserUpdateForm, PhoneUpdateForm, AddressUpdateForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as login_auth, logout as logout_auth, update_session_auth_hash
from django.core.cache import cache


# Create your views here.
def format_cpf(cpf_digits):
    if not cpf_digits or len(cpf_digits) != 11:
        return cpf_digits
    return f'{cpf_digits[0:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:11]}'


def build_cpf_candidates(cpf_raw):
    cpf_digits = re.sub(r'\D', '', cpf_raw or '')
    cpf_formatted = format_cpf(cpf_digits)
    return [value for value in [cpf_raw, cpf_digits, cpf_formatted] if value]

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        phone_form = PhoneRegisterForm(request.POST)
        address_form = AddressRegisterForm(request.POST)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if user_form.is_valid() and phone_form.is_valid() and address_form.is_valid():
            cpf_raw = user_form.cleaned_data['cpf']
            cpf_candidates = build_cpf_candidates(cpf_raw)
            cpf_exists = User.objects.filter(cpf__in=cpf_candidates).exists()
            if cpf_exists:
                message = 'Erro: CPF já registrado. Por favor, use outro CPF.'
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': message,
                        'errors': {
                            'cpf': [message]
                        }
                    }, status=400)
                return render(request, 'register.html', {
                    'user_form': user_form,
                    'phone_form': phone_form,
                    'address_form': address_form,
                    'message': message,
                    'message_type': 'error'
                })

            user = user_form.save(commit=False)
            cpf_digits = re.sub(r'\D', '', cpf_raw or '')
            if cpf_digits:
                user.cpf = cpf_digits
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            phone = phone_form.save(commit=False)
            phone.user = user
            phone.save()

            address = address_form.save(commit=False)
            address.user = user
            address.save()

            message = 'Usuário registrado com sucesso!'
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'redirect_url': reverse('authorization:login')
                })
            login_form = UserLoginForm()
            return render(request, 'login.html', {
                'login_form': login_form,
                'message': message,
                'message_type': 'success',
            })

        message = 'Erro ao registrar usuário. Verifique os dados e tente novamente.'
        if is_ajax:
            errors = {}
            for form in (user_form, phone_form, address_form):
                for field, field_errors in form.errors.get_json_data().items():
                    errors[field] = [error['message'] for error in field_errors]
            return JsonResponse({
                'success': False,
                'message': message,
                'errors': errors
            }, status=400)
        return render(request, 'register.html', {
            'user_form': user_form,
            'phone_form': phone_form,
            'address_form': address_form,
            'message': message,
            'message_type': 'error'
        })

    user_form = UserRegisterForm()
    phone_form = PhoneRegisterForm()
    address_form = AddressRegisterForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'phone_form': phone_form,
        'address_form': address_form,
    })

def login(request):
    if request.method == 'POST':
        login_form = UserLoginForm(request.POST)

        if login_form.is_valid():
            cpf_raw = login_form.cleaned_data['cpf']
            password = login_form.cleaned_data['password']
            cpf_candidates = build_cpf_candidates(cpf_raw)
            user = None
            # attempt authentication with each candidate (plain, digits, formatted)
            for cpf_value in cpf_candidates:
                user = authenticate(request, username=cpf_value, password=password)
                if user:
                    break
            if user is None:
                # last-resort: fetch user manually to check password for logging
                user = User.objects.filter(cpf__in=cpf_candidates).first()
                if user and not user.check_password(password):
                    user = None
            if user is None:
                # DEBUG log - show candidates and whether any user found
                import logging
                logger = logging.getLogger(__name__)
                logger.debug('Login failed for cpf_candidates=%s, user_found=%s', cpf_candidates, bool(User.objects.filter(cpf__in=cpf_candidates).exists()))

            if user is None:
                message = 'Erro: CPF ou senha inválidos.'
                return render(request, 'login.html', {
                    'login_form': login_form,
                    'message': message,
                    'message_type': 'error',
                })

            login_auth(request, user)

            if login_form.cleaned_data.get('remember_me'):
                request.session.set_expiry(60 * 60)
            else:
                request.session.set_expiry(0)

            message = 'Login bem-sucedido!'
            return render(request, 'profile.html', {
                'message': message,
                'message_type': 'success',
            })

        message = 'Erro ao fazer login. Verifique os dados e tente novamente.'
        return render(request, 'login.html', {
            'login_form': login_form,
            'message': message,
            'message_type': 'error',
        })

    login_form = UserLoginForm()
    return render(request, 'login.html', {
        'login_form': login_form,
    })

@login_required
def logout(request):
    logout_auth(request)
    message = 'Logout bem-sucedido!'
    login_form = UserLoginForm()
    return render(request, 'login.html', {
        'login_form': login_form,
        'message': message,
        'message_type': 'success'
    })

def password_reset(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)

        if password_reset_form.is_valid():
            email = password_reset_form.cleaned_data['email']
            password = password_reset_form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                message = 'Senha redefinida com sucesso!'
                password_reset_form = PasswordResetForm()
                return render(request, 'password-reset.html', {
                    'password_reset_form': password_reset_form,
                    'message': message,
                    'message_type': 'success'
                })
            except User.DoesNotExist:
                message = 'Erro: Usuário não encontrado com este e-mail.'
                return render(request, 'password-reset.html', {
                    'password_reset_form': password_reset_form,
                    'message': message,
                    'message_type': 'error'
                })
            except User.MultipleObjectsReturned:
                message = 'Erro: Múltiplos usuários encontrados com este e-mail. Entre em contato com o suporte.'
                return render(request, 'password-reset.html', {
                    'password_reset_form': password_reset_form,
                    'message': message,
                    'message_type': 'error'
                })

        message = 'Erro ao redefinir senha. Verifique os dados e tente novamente.'
        return render(request, 'password-reset.html', {
            'password_reset_form': password_reset_form,
            'message': message,
            'message_type': 'error'
        })

    password_reset_form = PasswordResetForm()
    return render(request, 'password-reset.html', {
        'password_reset_form': password_reset_form
    })

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def update_profile(request):
    phone_instance = request.user.phones.first()
    address_instance = request.user.addresses.first()

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        phone_form = PhoneUpdateForm(request.POST, instance=phone_instance)
        address_form = AddressUpdateForm(request.POST, instance=address_instance)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if user_form.is_valid() and phone_form.is_valid() and address_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
                update_session_auth_hash(request, user)
            else:
                user.password = request.user.password
            user.save()

            phone = phone_form.save(commit=False)
            phone.user = request.user
            phone.save()

            address = address_form.save(commit=False)
            address.user = request.user
            address.save()

            message = 'Perfil atualizado com sucesso!'
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'redirect_url': reverse('authorization:profile')
                })
            return render(request, 'profile.html', {
                'user_form': user_form,
                'phone_form': phone_form,
                'address_form': address_form,
                'message': message,
                'message_type': 'success'
            })

        message = 'Erro ao atualizar perfil. Verifique os dados e tente novamente.'
        if is_ajax:
            errors = {}
            for form in (user_form, phone_form, address_form):
                for field, field_errors in form.errors.get_json_data().items():
                    errors[field] = [error['message'] for error in field_errors]
            return JsonResponse({
                'success': False,
                'message': message,
                'errors': errors
            }, status=400)
        return render(request, 'update-profile.html', {
            'user_form': user_form,
            'phone_form': phone_form,
            'address_form': address_form,
            'message': message,
            'message_type': 'error'
        })

    user_form = UserUpdateForm(instance=request.user)
    phone_form = PhoneUpdateForm(instance=phone_instance)
    address_form = AddressUpdateForm(instance=address_instance)

    return render(request, 'update-profile.html', {
        'user_form': user_form,
        'phone_form': phone_form,
        'address_form': address_form,
    })
