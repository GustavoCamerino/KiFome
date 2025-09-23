from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from clientes.models import Cliente
from restaurantes.models import Restaurante, Prato


STATUS_CHOICES = [
    ('pendente', 'Pendente'),
    ('preparacao', 'Preparação'),
    ('transito', 'Trânsito'),
    ('entregue', 'Entregue'),
    ('cancelado', 'Cancelado'),
]


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='pedidos')
    data_hora = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    forma_pagamento = models.CharField(max_length=50, default='simulado')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    endereco_entrega = models.TextField(blank=True)

    @property
    def comissao_plataforma(self):
        # 3% de comissão usando Decimal
        if self.valor_total is None:
            return Decimal('0.00')
        return (self.valor_total * Decimal('0.03')).quantize(Decimal('0.01'))

    @property
    def valor_liquido_restaurante(self):
        # Valor após comissão (quando concluído)
        if self.valor_total is None:
            return Decimal('0.00')
        return (self.valor_total * Decimal('0.97')).quantize(Decimal('0.01'))

    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.cliente.nome_completo}"


class ItemPedido(models.Model):
    id_item = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    prato = models.ForeignKey(Prato, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    observacao = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quantidade}x {self.prato.nome} (Pedido {self.pedido_id})"
