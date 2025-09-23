from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from clientes.models import Cliente
from restaurantes.models import Restaurante


class AvaliacaoRestaurante(models.Model):
    id_avaliacao = models.AutoField(primary_key=True)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='avaliacoes')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='avaliacoes')
    nota = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    feedback = models.TextField(blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurante.nome} - {self.nota}/5"

