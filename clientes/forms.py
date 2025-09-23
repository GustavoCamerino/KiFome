from django import forms
from django.contrib.auth.models import User
from .models import Cliente
from .models import EnderecoEntrega


class ClienteSignupForm(forms.Form):
    nome_completo = forms.CharField(max_length=255)
    email = forms.EmailField()
    telefone = forms.CharField(max_length=20, required=False)
    cpf = forms.CharField(max_length=14, required=False)
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
        cliente = Cliente.objects.create(
            user=user,
            nome_completo=data['nome_completo'],
            email=data['email'],
            telefone=data.get('telefone', ''),
            cpf=data.get('cpf', ''),
            foto=self.cleaned_data.get('foto'),
        )
        return user, cliente


class ClienteProfileForm(forms.ModelForm):
    endereco = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)

    class Meta:
        model = Cliente
        fields = ['nome_completo', 'telefone', 'cpf', 'foto']

    def save(self, commit=True):
        cliente = super().save(commit)
        endereco_txt = self.cleaned_data.get('endereco', '').strip()
        if endereco_txt:
            addr = cliente.enderecos.first()
            if addr:
                addr.endereco = endereco_txt
                addr.save()
            else:
                EnderecoEntrega.objects.create(cliente=cliente, endereco=endereco_txt)
        return cliente
