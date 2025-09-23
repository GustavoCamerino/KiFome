from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ClienteSignupForm, ClienteProfileForm
from pedidos.models import Pedido


def cliente_signup(request):
    if request.method == 'POST':
        form = ClienteSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user, _cliente = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = ClienteSignupForm()
    return render(request, 'clientes/signup.html', {'form': form})


@login_required
def cliente_dashboard(request):
    if not hasattr(request.user, 'cliente'):
        return redirect('home')
    cliente = request.user.cliente
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-data_hora')
    return render(request, 'clientes/dashboard.html', {'cliente': cliente, 'pedidos': pedidos})


@login_required
def cliente_profile(request):
    if not hasattr(request.user, 'cliente'):
        return redirect('home')
    cliente = request.user.cliente
    initial = {}
    if cliente.enderecos.exists():
        initial['endereco'] = cliente.enderecos.first().endereco
    if request.method == 'POST':
        form = ClienteProfileForm(request.POST, request.FILES, instance=cliente, initial=initial)
        if form.is_valid():
            form.save()
            return redirect('cliente_dashboard')
    else:
        form = ClienteProfileForm(instance=cliente, initial=initial)
    return render(request, 'clientes/perfil.html', {'form': form, 'cliente': cliente})
