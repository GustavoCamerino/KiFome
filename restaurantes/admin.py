from django.contrib import admin
from .models import Restaurante, HorarioFuncionamentoRestaurante, CategoriaPrato, Prato


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ("id_restaurante", "nome", "endereco", "tipo_culinaria")
    search_fields = ("nome", "tipo_culinaria")


@admin.register(HorarioFuncionamentoRestaurante)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("restaurante", "dia_semana", "horario_abertura", "horario_fechamento")
    list_filter = ("dia_semana",)


@admin.register(CategoriaPrato)
class CategoriaPratoAdmin(admin.ModelAdmin):
    list_display = ("id_categoria", "nome_categoria")
    search_fields = ("nome_categoria",)


@admin.register(Prato)
class PratoAdmin(admin.ModelAdmin):
    list_display = ("id_prato", "nome", "restaurante", "categoria", "preco", "disponibilidade", "estoque")
    list_filter = ("disponibilidade", "categoria")
    search_fields = ("nome", "restaurante__nome")

