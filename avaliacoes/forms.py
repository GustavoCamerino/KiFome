from django import forms
from .models import AvaliacaoRestaurante


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoRestaurante
        fields = ['nota', 'feedback']

