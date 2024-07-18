from django import forms
from django.core.exceptions import ValidationError
from .models import UserTwoFactorAuthData

class SignupForm(forms.Form):
    fname = forms.CharField(label='Prenom', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre prénom '}))
    lname = forms.CharField(label='Nom', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre nom'}))
    email = forms.EmailField(label='Adresse email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre email'}))
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mot de passe'}))
    accept_terms = forms.BooleanField(label="J'accepte les termes et conditions", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'checkbox-signup'}))


class LoginForm(forms.Form):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control',"placeholder": "Votre addresse email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder": "Votre mode passe"}))


class TwoFactorAuthForm(forms.Form):
    otp = forms.CharField(required=True)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_otp(self):
        two_factor_auth_data = UserTwoFactorAuthData.objects.filter(user=self.user).first()

        if two_factor_auth_data is None:
            raise ValidationError('2FA not set up.')

        otp = self.cleaned_data.get('otp')

        if not two_factor_auth_data.validate_otp(otp):
            raise ValidationError('Invalid 2FA code.')

        return otp