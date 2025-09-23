from django import forms


FORMA_PAGAMENTO_CHOICES = [
    ('simulado_cartao', 'Cartão (simulado)'),
    ('simulado_pix', 'PIX (simulado)'),
    ('simulado_dinheiro', 'Dinheiro (simulado)'),
]


class CheckoutForm(forms.Form):
    endereco_entrega = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    forma_pagamento = forms.ChoiceField(choices=FORMA_PAGAMENTO_CHOICES)

