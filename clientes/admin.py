from django.contrib import admin
from .models import Cliente, EnderecoEntrega


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id_cliente", "nome_completo", "email")
    search_fields = ("nome_completo", "email")


@admin.register(EnderecoEntrega)
class EnderecoEntregaAdmin(admin.ModelAdmin):
    list_display = ("id_endereco", "cliente", "endereco")
    search_fields = ("cliente__nome_completo", "endereco")

