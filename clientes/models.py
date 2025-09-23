from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    nome_completo = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=14, blank=True)
    foto = models.ImageField(upload_to='clientes/', blank=True, null=True)

    def __str__(self):
        return self.nome_completo


class EnderecoEntrega(models.Model):
    id_endereco = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='enderecos')
    endereco = models.TextField()

    def __str__(self):
        return f"{self.cliente.nome_completo} - {self.endereco[:30]}"
