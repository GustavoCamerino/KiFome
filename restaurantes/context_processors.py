from .models import Restaurante


def nav_restaurantes(request):
    try:
        items = Restaurante.objects.all().order_by('nome')[:8]
    except Exception:
        items = []
    return {
        'nav_restaurantes': items
    }

