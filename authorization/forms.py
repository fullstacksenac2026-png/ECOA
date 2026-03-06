
import re

from django import forms
from .models import User, Phone, Address, GENDER_CHOICES, SEXUALITY_CHOICES
from django.core.validators import RegexValidator


# login does not create or modify a User instance, so use simple Form
class UserLoginForm(forms.Form):
    remember_me = forms.BooleanField(label='Lembrar-me', widget=forms.CheckboxInput(attrs={'class': 'form-check-input border-3 border black'}), required=False)
    cpf = forms.CharField(
        label='CPF',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00'
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'})
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '') or ''
        cpf = cpf.strip()
        cpf_digits = re.sub(r'\D', '', cpf)
        if not cpf_digits:
            raise forms.ValidationError('O campo de CPF é obrigatório.')
        if len(cpf_digits) != 11:
            raise forms.ValidationError('O CPF deve conter 11 dígitos.')
        return cpf_digits

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password') or ''
        # We generally should NOT strip the password as it could be intentional,
        # but if we do, it must be consistent with registration.
        # Let's keep it as is from the input to avoid issues with specialized passwords.
        cleaned_data['password'] = password

        if not password or len(password) < 8:
            self.add_error('password', 'A senha deve conter pelo menos 8 caracteres.')

        return cleaned_data


class UserRegisterForm(forms.ModelForm):
    
    cpf = forms.CharField(
        label='CPF',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00'
        })
    )
    confirm_password = forms.CharField(max_length=255, label='Confirmar Senha', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'},),)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'cpf', 'birth_date', 'gender', 'sexuality']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'},),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'},),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@gmail.com'},),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********', 'min_length': 8}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'dd/mm/yyyy'},),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=GENDER_CHOICES),
            'sexuality': forms.Select(attrs={'class': 'form-control'}, choices=SEXUALITY_CHOICES),
        }
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'Email',
            'password': 'Senha',
            'birth_date': 'Data de Nascimento',
            'gender': 'Gênero',
            'sexuality': 'Sexualidade',
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '') or ''
        cpf_digits = re.sub(r'\D', '', cpf)
        if not cpf_digits:
            raise forms.ValidationError('O campo de CPF é obrigatório.')
        if len(cpf_digits) != 11:
            raise forms.ValidationError('O CPF deve conter 11 dígitos.')
        return cpf_digits

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        cpf = cleaned_data.get('cpf') # This will be the cleaned digits if clean_cpf ran
        birth_date = cleaned_data.get('birth_date')
        gender = cleaned_data.get('gender')
        sexuality = cleaned_data.get('sexuality')

        if not first_name:
            self.add_error('first_name', 'O campo de nome é obrigatório.')

        if not last_name:
            self.add_error('last_name', 'O campo de sobrenome é obrigatório.')

        if not email:
            self.add_error('email', 'O campo de email é obrigatório.')

        if not password or len(password) < 8:
            self.add_error('password', 'A senha deve conter pelo menos 8 caracteres.')

        if confirm_password and len(confirm_password) < 8:
            self.add_error('confirm_password', 'A senha deve conter pelo menos 8 caracteres.')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'As senhas não coincidem.')

        # Verification already handled in clean_cpf, but we can do a secondary check if needed
        if not cpf:
             self.add_error('cpf', 'O campo de CPF é obrigatório.')

        if not birth_date:
            self.add_error('birth_date', 'O campo de data de nascimento é obrigatório.')

        if not gender:
            self.add_error('gender', 'O campo de gênero é obrigatório.')

        if not sexuality:
            self.add_error('sexuality', 'O campo de sexualidade é obrigatório.')

        return cleaned_data


class PhoneRegisterForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['ddi', 'ddd', 'phone_number', 'is_mobile']
        widgets = {
            'ddi': forms.Select(attrs={'class': 'form-control', 'id': 'ddi-select', 'aria-label': 'País (DDI)'},),
            'ddd': forms.Select(attrs={'class': 'form-control', 'id': 'ddd-select', 'aria-label': 'Estado ou província (DDD)'},),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'phone-input',
                'placeholder': '00000-0000',
                'inputmode': 'numeric',
                'pattern': r'\d{5}-\d{4}',
                'aria-label': 'Número de telefone',
            },),
            'is_mobile': forms.CheckboxInput(attrs={'class': 'form-check-input'},),
        }
        labels = {
            'ddi': 'DDI',
            'ddd': 'DDD',
            'phone_number': 'Número de Telefone',
            'is_mobile': 'É um telefone móvel?',
        }

    def clean(self):
        cleaned_data = super().clean()
        ddi = cleaned_data.get('ddi')
        ddd = cleaned_data.get('ddd')
        phone_number = cleaned_data.get('phone_number')
        is_mobile = cleaned_data.get('is_mobile')

        if not ddi:
            self.add_error('ddi', 'O campo de DDI é obrigatório.')

        if not ddd:
            self.add_error('ddd', 'O campo de DDD é obrigatório.')

        if not phone_number:
            self.add_error('phone_number', 'O campo de número de telefone é obrigatório.')

        if phone_number and not re.match(r'^\d{5}-\d{4}$', phone_number):
            self.add_error('phone_number', 'O telefone deve estar no formato 00000-0000.')

        if is_mobile is None:
            self.add_error('is_mobile', 'O campo de telefone móvel é obrigatório.')

        return cleaned_data


class AddressRegisterForm(forms.ModelForm):
    cep = forms.CharField(
        label='CEP',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00'
        })
    )

    class Meta:
        model = Address
        fields = ['residence_number', 'complement', 'street', 'neighborhood', 'city', 'state', 'country']
        widgets = {
            'residence_number': forms.TextInput(attrs={'class': 'form-control'},),
            'complement': forms.TextInput(attrs={'class': 'form-control'},),
            'street': forms.TextInput(attrs={'class': 'form-control'},),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'},),
            'city': forms.Select(attrs={'class': 'form-control', 'id': 'address-city-select'},),
            'state': forms.Select(attrs={'class': 'form-control', 'id': 'address-state-select'},),
            'country': forms.Select(attrs={'class': 'form-control', 'id': 'address-country-select'},),
        }
        labels = {
            'residence_number': 'Número da Residência',
            'complement': 'Complemento',
            'street': 'Rua',
            'neighborhood': 'Bairro',
            'city': 'Cidade',
            'state': 'Estado',
            'country': 'País',
        }

    def clean(self):
        cleaned_data = super().clean()
        cep = cleaned_data.get('cep')
        residence_number = cleaned_data.get('residence_number')
        street = cleaned_data.get('street')
        neighborhood = cleaned_data.get('neighborhood')
        city = cleaned_data.get('city')
        state = cleaned_data.get('state')
        country = cleaned_data.get('country')

        if not cep:
            self.add_error('cep', 'O campo de CEP é obrigatório.')

        if not residence_number:
            self.add_error('residence_number', 'O campo de número da residência é obrigatório.')

        if not street:
            self.add_error('street', 'O campo de rua é obrigatório.')

        if not neighborhood:
            self.add_error('neighborhood', 'O campo de bairro é obrigatório.')

        if not city:
            self.add_error('city', 'O campo de cidade é obrigatório.')

        if not state:
            self.add_error('state', 'O campo de estado é obrigatório.')

        if not country:
            self.add_error('country', 'O campo de país é obrigatório.')

        return cleaned_data

class PasswordResetForm(forms.ModelForm):

    confirm_password = forms.CharField(max_length=255, label='Confirmar Senha', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'},),)

    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@gmail.com'},),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'},),
        }
        labels = {
            'email': 'Email',
            'password': 'Senha',
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if not email:
            self.add_error('email', 'O email é obrigatório.')
        
        if password and len(password) < 8:
            self.add_error('password', 'A senha deve conter pelo menos 8 caracteres.')

        if confirm_password and len(confirm_password) < 8:
            self.add_error('confirm_password', 'A senha deve conter pelo menos 8 caracteres.')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'As senhas não coincidem.')

        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    cpf = forms.CharField(
        label='CPF',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00'
        })
    )
    password = forms.CharField(
        label='Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'},),
    )
    confirm_password = forms.CharField(
        max_length=255,
        label='Confirmar Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'},),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'cpf', 'birth_date', 'gender', 'sexuality']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'},),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'},),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemplo@gmail.com'},),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'dd/mm/yyyy'},),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=GENDER_CHOICES),
            'sexuality': forms.Select(attrs={'class': 'form-control'}, choices=SEXUALITY_CHOICES),
        }
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'Email',
            'password': 'Senha',
            'birth_date': 'Data de Nascimento',
            'gender': 'Gênero',
            'sexuality': 'Sexualidade',
        }

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        birth_date = cleaned_data.get('birth_date')
        gender = cleaned_data.get('gender')
        sexuality = cleaned_data.get('sexuality')

        if not first_name:
            self.add_error('first_name', 'O campo de nome é obrigatório.')

        if not last_name:
            self.add_error('last_name', 'O campo de sobrenome é obrigatório.')

        if not email:
            self.add_error('email', 'O campo de email é obrigatório.')

        if password and len(password) < 8:
            self.add_error('password', 'A senha deve conter pelo menos 8 caracteres.')

        if confirm_password and len(confirm_password) < 8:
            self.add_error('confirm_password', 'A senha deve conter pelo menos 8 caracteres.')

        if password or confirm_password:
            if not confirm_password:
                self.add_error('confirm_password', 'Confirme a senha.')
            elif password != confirm_password:
                self.add_error('confirm_password', 'As senhas não coincidem.')

        if not birth_date:
            self.add_error('birth_date', 'O campo de data de nascimento é obrigatório.')

        if not gender:
            self.add_error('gender', 'O campo de gênero é obrigatório.')

        if not sexuality:
            self.add_error('sexuality', 'O campo de sexualidade é obrigatório.')

        return cleaned_data

class PhoneUpdateForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['ddi', 'ddd', 'phone_number']
        widgets = {
            'ddi': forms.Select(attrs={'class': 'form-control', 'id': 'ddi-select', 'aria-label': 'País (DDI)'},),
            'ddd': forms.Select(attrs={'class': 'form-control', 'id': 'ddd-select', 'aria-label': 'Estado ou província (DDD)'},),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'phone-input',
                'placeholder': '00000-0000',
                'inputmode': 'numeric',
                'pattern': r'\d{5}-\d{4}',
                'aria-label': 'Número de telefone',
            },),
        }
        labels = {
            'ddi': 'DDI',
            'ddd': 'DDD',
            'phone_number': 'Número de Telefone',
        }

class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['cep', 'residence_number', 'complement', 'street', 'neighborhood', 'city', 'state', 'country']
        widgets = {
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'},),
            'residence_number': forms.TextInput(attrs={'class': 'form-control'},),
            'complement': forms.TextInput(attrs={'class': 'form-control'},),
            'street': forms.TextInput(attrs={'class': 'form-control'},),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'},),
            'city': forms.Select(attrs={'class': 'form-control', 'id': 'address-city-select'},),
            'state': forms.Select(attrs={'class': 'form-control', 'id': 'address-state-select'},),
            'country': forms.Select(attrs={'class': 'form-control', 'id': 'address-country-select'},),
        }
        labels = {
            'cep': 'CEP',
            'residence_number': 'Número da Residência',
            'complement': 'Complemento',
            'street': 'Rua',
            'neighborhood': 'Bairro',
            'city': 'Cidade',
            'state': 'Estado',
            'country': 'País',
        }
