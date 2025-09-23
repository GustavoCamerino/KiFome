from django import forms
from django.contrib.auth.models import User
from .models import Restaurante, Prato
from .models import CategoriaPrato


class RestauranteSignupForm(forms.Form):
    nome = forms.CharField(max_length=255)
    endereco = forms.CharField(max_length=255)
    telefone = forms.CharField(max_length=20, required=False)
    tipo_culinaria = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    foto = forms.ImageField(required=False)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email já cadastrado.')
        return email

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password']
        )
        restaurante = Restaurante.objects.create(
            user=user,
            nome=data['nome'],
            endereco=data['endereco'],
            telefone=data.get('telefone', ''),
            tipo_culinaria=data.get('tipo_culinaria', ''),
            foto=self.cleaned_data.get('foto'),
        )
        return user, restaurante


class PratoForm(forms.ModelForm):
    class Meta:
        model = Prato
        fields = ['categoria', 'nome', 'descricao', 'preco', 'disponibilidade', 'estoque', 'foto']


class CategoriaPratoForm(forms.ModelForm):
    class Meta:
        model = CategoriaPrato
        fields = ['nome_categoria']


class RestauranteProfileForm(forms.ModelForm):
    class Meta:
        model = Restaurante
        fields = ['nome', 'endereco', 'telefone', 'tipo_culinaria', 'foto']
