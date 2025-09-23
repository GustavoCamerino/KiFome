from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from restaurantes.models import Restaurante
from .forms import AvaliacaoForm
from .models import AvaliacaoRestaurante


@login_required
def avaliar_restaurante(request, restaurante_id):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, 'Apenas clientes podem avaliar restaurantes.')
        return redirect('home')
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.restaurante = restaurante
            avaliacao.cliente = request.user.cliente
            avaliacao.save()
            messages.success(request, 'Avaliação enviada!')
            return redirect('restaurante_detail', restaurante_id=restaurante_id)
    else:
        form = AvaliacaoForm()
    return render(request, 'avaliacoes/form.html', {'form': form, 'restaurante': restaurante})

