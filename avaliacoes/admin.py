from django.contrib import admin
from .models import AvaliacaoRestaurante


@admin.register(AvaliacaoRestaurante)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("id_avaliacao", "restaurante", "cliente", "nota", "data_hora")
    list_filter = ("nota",)
    search_fields = ("restaurante__nome", "cliente__nome_completo")

