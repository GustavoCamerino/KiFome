from django.db import models
from django.contrib.auth.models import User


DIA_SEMANA_CHOICES = [
    ("Segunda", "Segunda"),
    ("Terça", "Terça"),
    ("Quarta", "Quarta"),
    ("Quinta", "Quinta"),
    ("Sexta", "Sexta"),
    ("Sábado", "Sábado"),
    ("Domingo", "Domingo"),
]


class Restaurante(models.Model):
    id_restaurante = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurante')
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True)
    tipo_culinaria = models.CharField(max_length=100, blank=True)
    foto = models.ImageField(upload_to='restaurantes/', blank=True, null=True)

    def __str__(self):
        return self.nome


class HorarioFuncionamentoRestaurante(models.Model):
    id_horario_funcionamento = models.AutoField(primary_key=True)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(max_length=10, choices=DIA_SEMANA_CHOICES)
    horario_abertura = models.TimeField()
    horario_fechamento = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['restaurante', 'dia_semana'], name='unique_restaurante_dia')
        ]

    def __str__(self):
        return f"{self.restaurante.nome} - {self.dia_semana}"


class CategoriaPrato(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome_categoria


class Prato(models.Model):
    id_prato = models.AutoField(primary_key=True)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='pratos')
    categoria = models.ForeignKey(CategoriaPrato, on_delete=models.SET_NULL, null=True, related_name='pratos')
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilidade = models.BooleanField(default=True)
    estoque = models.PositiveIntegerField(default=0)
    foto = models.ImageField(upload_to='pratos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.restaurante.nome})"
