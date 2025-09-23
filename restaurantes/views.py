from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Restaurante, Prato, CategoriaPrato
from .forms import RestauranteSignupForm, PratoForm, CategoriaPratoForm, RestauranteProfileForm


def home(request):
    restaurantes = Restaurante.objects.all()
    return render(request, 'home.html', {'restaurantes': restaurantes})


def restaurante_detail(request, restaurante_id):
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    categorias = CategoriaPrato.objects.all().order_by('nome_categoria')
    pratos_por_cat = []
    for cat in categorias:
        pratos = restaurante.pratos.filter(categoria=cat, disponibilidade=True).order_by('nome')
        if pratos.exists():
            pratos_por_cat.append((cat, pratos))
    return render(request, 'restaurantes/detail.html', {
        'restaurante': restaurante,
        'pratos_por_cat': pratos_por_cat,
    })


def restaurante_signup(request):
    if request.method == 'POST':
        form = RestauranteSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user, _rest = form.save()
            login(request, user)
            return redirect('restaurante_dashboard')
    else:
        form = RestauranteSignupForm()
    return render(request, 'restaurantes/signup.html', {'form': form})


@login_required
def restaurante_dashboard(request):
    if not hasattr(request.user, 'restaurante'):
        return redirect('home')
    restaurante = request.user.restaurante
    pratos = restaurante.pratos.all().order_by('nome')
    # Pedidos e lucro (valor líqüido após 3%)
    from pedidos.models import Pedido
    pedidos = Pedido.objects.filter(restaurante=restaurante).order_by('-data_hora')[:25]
    lucro = sum([p.valor_liquido_restaurante for p in Pedido.objects.filter(restaurante=restaurante, status='entregue')])
    return render(request, 'restaurantes/dashboard.html', {'restaurante': restaurante, 'pratos': pratos, 'pedidos': pedidos, 'lucro': lucro})


@login_required
def prato_create(request):
    if not hasattr(request.user, 'restaurante'):
        return redirect('home')
    restaurante = request.user.restaurante
    if request.method == 'POST':
        form = PratoForm(request.POST, request.FILES)
        if form.is_valid():
            prato = form.save(commit=False)
            prato.restaurante = restaurante
            prato.save()
            return redirect('restaurante_dashboard')
    else:
        form = PratoForm()
    # opcional: limitar categorias visÃ­veis (a todas existentes por enquanto)
    return render(request, 'restaurantes/prato_form.html', {'form': form, 'acao': 'Novo Prato'})


@login_required
def prato_edit(request, prato_id):
    if not hasattr(request.user, 'restaurante'):
        return redirect('home')
    restaurante = request.user.restaurante
    prato = get_object_or_404(Prato, pk=prato_id, restaurante=restaurante)
    if request.method == 'POST':
        form = PratoForm(request.POST, request.FILES, instance=prato)
        if form.is_valid():
            form.save()
            return redirect('restaurante_dashboard')
    else:
        form = PratoForm(instance=prato)
    return render(request, 'restaurantes/prato_form.html', {'form': form, 'acao': 'Editar Prato'})


@login_required
def categorias_manage(request):
    if not hasattr(request.user, 'restaurante'):
        return redirect('home')
    restaurante = request.user.restaurante
    msg = None
    if request.method == 'POST':
        form = CategoriaPratoForm(request.POST)
        if form.is_valid():
            from .models import CategoriaPrato
            nome = form.cleaned_data['nome_categoria']
            obj, created = CategoriaPrato.objects.get_or_create(nome_categoria=nome)
            msg = 'Categoria criada com sucesso.' if created else 'Categoria jÃ¡ existia e foi reutilizada.'
            form = CategoriaPratoForm()
    else:
        form = CategoriaPratoForm()
    # categorias atualmente usadas pelo restaurante
    usadas = set(restaurante.pratos.filter(categoria__isnull=False).values_list('categoria__nome_categoria', flat=True))
    from .models import CategoriaPrato
    todas = CategoriaPrato.objects.all().order_by('nome_categoria')
    return render(request, 'restaurantes/categorias.html', {
        'restaurante': restaurante,
        'form': form,
        'mensagem': msg,
        'categorias_usadas': usadas,
        'todas_categorias': todas,
    })


@login_required
def restaurante_profile(request):
    if not hasattr(request.user, 'restaurante'):
        return redirect('home')
    restaurante = request.user.restaurante
    if request.method == 'POST':
        form = RestauranteProfileForm(request.POST, request.FILES, instance=restaurante)
        if form.is_valid():
            form.save()
            return redirect('restaurante_dashboard')
    else:
        form = RestauranteProfileForm(instance=restaurante)
    return render(request, 'restaurantes/perfil.html', {'form': form, 'restaurante': restaurante})


@login_required
def prato_delete(request, prato_id):
    if not hasattr(request.user, 'restaurante'):
        return redirect('home')
    restaurante = request.user.restaurante
    prato = get_object_or_404(Prato, pk=prato_id, restaurante=restaurante)
    if request.method == 'POST':
        prato.delete()
        return redirect('restaurante_dashboard')
    return render(request, 'restaurantes/prato_delete_confirm.html', {'prato': prato})


@login_required
def dashboard_data(request):
    # Somente restaurante dono
    if not hasattr(request.user, 'restaurante'):
        return JsonResponse({'error': 'forbidden'}, status=403)
    restaurante = request.user.restaurante
    from pedidos.models import Pedido
    pedidos = Pedido.objects.filter(restaurante=restaurante).order_by('-data_hora')[:25]
    lucro = sum([p.valor_liquido_restaurante for p in Pedido.objects.filter(restaurante=restaurante, status='entregue')])

    def item_dict(item):
        return {
            'quantidade': item.quantidade,
            'prato_nome': item.prato.nome,
            'prato_foto': item.prato.foto.url if getattr(item.prato, 'foto') else '',
        }

    data = {
        'lucro': f"{lucro}",
        'pedidos': [
            {
                'id': p.id_pedido,
                'status': p.status,
                'status_display': p.get_status_display(),
                'valor_total': f"{p.valor_total}",
                'endereco_entrega': p.endereco_entrega or '',
                'cliente_nome': p.cliente.nome_completo,
                'cliente_foto': p.cliente.foto.url if getattr(p.cliente, 'foto') else '',
                'itens': [item_dict(it) for it in p.itens.all()],
            }
            for p in pedidos
        ],
    }
    return JsonResponse(data)
