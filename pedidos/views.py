from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from restaurantes.models import Prato, Restaurante
from .forms import CheckoutForm
from .models import Pedido, ItemPedido
from django.http import JsonResponse


def _get_cart(session):
    return session.setdefault('cart', {})


def _cart_summary(session):
    cart = session.get('cart', {})
    count = sum(cart.values())
    total = Decimal('0.00')
    for pid, qty in cart.items():
        try:
            p = Prato.objects.get(pk=int(pid))
            total += p.preco * qty
        except Prato.DoesNotExist:
            pass
    return count, total


@login_required
def add_to_cart(request, prato_id):
    prato = get_object_or_404(Prato, pk=prato_id, disponibilidade=True)
    cart = _get_cart(request.session)
    try:
        qty = int(request.GET.get('qty', '1'))
    except ValueError:
        qty = 1
    if qty < 1:
        qty = 1
    # Checar estoque e decrementar imediatamente
    if prato.estoque < qty:
        msg = 'Estoque insuficiente.'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({'ok': False, 'error': msg}, status=400)
        messages.error(request, msg)
        return redirect('restaurante_detail', restaurante_id=prato.restaurante_id)
    prato.estoque -= qty
    if prato.estoque == 0:
        prato.disponibilidade = False
    prato.save()
    cart[str(prato_id)] = cart.get(str(prato_id), 0) + qty
    request.session.modified = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        count, total = _cart_summary(request.session)
        return JsonResponse({'ok': True, 'count': count, 'total': str(total)})
    messages.success(request, f"{prato.nome} adicionado ao carrinho!")
    return redirect('restaurante_detail', restaurante_id=prato.restaurante_id)


def remove_from_cart(request, prato_id):
    cart = _get_cart(request.session)
    key = str(prato_id)
    qty = cart.get(key, 0)
    cart.pop(key, None)
    # Repor estoque quando remover do carrinho
    if qty:
        try:
            p = Prato.objects.get(pk=int(prato_id))
            p.estoque += qty
            if p.estoque > 0:
                p.disponibilidade = True
            p.save()
        except Prato.DoesNotExist:
            pass
    request.session.modified = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        count, total = _cart_summary(request.session)
        return JsonResponse({'ok': True, 'count': count, 'total': str(total)})
    return redirect('view_cart')


def view_cart(request):
    cart = _get_cart(request.session)
    items = []
    total = Decimal('0.00')
    restaurante = None
    for pid, qty in cart.items():
        prato = get_object_or_404(Prato, pk=int(pid))
        if restaurante is None:
            restaurante = prato.restaurante
        items.append({'prato': prato, 'quantidade': qty, 'subtotal': prato.preco * qty})
        total += prato.preco * qty
    return render(request, 'pedidos/cart.html', {'items': items, 'total': total, 'restaurante': restaurante})


@login_required
def buy_now(request, prato_id):
    # Busca o prato mesmo que disponibilidade esteja True/False e valida manualmente
    prato = get_object_or_404(Prato, pk=prato_id)
    if not prato.disponibilidade or prato.estoque < 1:
        messages.error(request, 'Produto indisponível no momento.')
        return redirect('restaurante_detail', restaurante_id=prato.restaurante_id)
    # Decrementa estoque de 1 unidade e coloca no carrinho
    if prato.estoque < 1:
        messages.error(request, 'Estoque insuficiente.')
        return redirect('restaurante_detail', restaurante_id=prato.restaurante_id)
    prato.estoque -= 1
    if prato.estoque == 0:
        prato.disponibilidade = False
    prato.save()
    request.session['cart'] = {str(prato_id): 1}
    request.session.modified = True
    return redirect('checkout')


@login_required
def checkout(request):
    if not hasattr(request.user, 'cliente'):
        messages.error(request, 'Você precisa estar logado como cliente para finalizar o pedido.')
        return redirect('view_cart')
    cart = _get_cart(request.session)
    if not cart:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('view_cart')
    # Verificar restaurante único
    restaurante = None
    pratos = []
    for pid, qty in cart.items():
        prato = get_object_or_404(Prato, pk=int(pid))
        pratos.append((prato, qty))
        if restaurante is None:
            restaurante = prato.restaurante
        elif restaurante != prato.restaurante:
            messages.error(request, 'O carrinho deve conter itens de um único restaurante.')
            return redirect('view_cart')
    total = sum(p.preco * qty for p, qty in pratos)

    # Formulário de checkout (endereço e pagamento)
    initial_address = ''
    if request.user.cliente.enderecos.exists():
        initial_address = request.user.cliente.enderecos.first().endereco

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            pedido = Pedido.objects.create(
                cliente=request.user.cliente,
                restaurante=restaurante,
                valor_total=total,
                forma_pagamento=form.cleaned_data['forma_pagamento'],
                status='pendente',
                endereco_entrega=form.cleaned_data['endereco_entrega'] or initial_address,
            )
            for p, qty in pratos:
                # Estoque já foi debitado ao adicionar ao carrinho.
                ItemPedido.objects.create(
                    pedido=pedido,
                    prato=p,
                    quantidade=qty,
                    preco_unitario=p.preco,
                )
            # Limpa carrinho
            request.session['cart'] = {}
            request.session.modified = True
            return redirect('order_tracking', pedido_id=pedido.id_pedido)
    else:
        form = CheckoutForm(initial={'endereco_entrega': initial_address})

    return render(request, 'pedidos/checkout.html', {
        'items': pratos,
        'total': total,
        'restaurante': restaurante,
        'form': form,
    })


@login_required
def order_tracking(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    # Permitir que cliente dono ou restaurante dono visualize
    if hasattr(request.user, 'cliente') and pedido.cliente != request.user.cliente:
        return redirect('home')
    if hasattr(request.user, 'restaurante') and pedido.restaurante != request.user.restaurante:
        return redirect('home')
    is_cliente_owner = hasattr(request.user, 'cliente') and pedido.cliente == getattr(request.user, 'cliente', None)
    is_restaurant_owner = hasattr(request.user, 'restaurante') and pedido.restaurante == getattr(request.user, 'restaurante', None)
    return render(request, 'pedidos/tracking.html', {
        'pedido': pedido,
        'is_cliente_owner': is_cliente_owner,
        'is_restaurant_owner': is_restaurant_owner,
    })


@login_required
def advance_status(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    # Somente o restaurante dono pode avançar o status
    if not hasattr(request.user, 'restaurante'):
        return redirect('home')
    if pedido.restaurante != request.user.restaurante:
        return redirect('home')
    next_map = {
        'pendente': 'preparacao',
        'preparacao': 'transito',
        'transito': 'entregue',
        'entregue': 'entregue',
    }
    pedido.status = next_map.get(pedido.status, 'entregue')
    pedido.save()
    return redirect('order_tracking', pedido_id=pedido.id_pedido)


@login_required
def cancel_order(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    # Apenas cliente dono pode cancelar e apenas se ainda não entregue/cancelado
    if not hasattr(request.user, 'cliente') or pedido.cliente != request.user.cliente:
        return redirect('home')
    if pedido.status in ['entregue', 'cancelado']:
        return redirect('order_tracking', pedido_id=pedido.id_pedido)
    if request.method == 'POST':
        # Repor estoque
        for item in pedido.itens.all():
            p = item.prato
            p.estoque += item.quantidade
            if p.estoque > 0:
                p.disponibilidade = True
            p.save()
        pedido.status = 'cancelado'
        pedido.save()
        messages.success(request, 'Pedido cancelado e estoque atualizado.')
        return redirect('order_tracking', pedido_id=pedido.id_pedido)
    return render(request, 'pedidos/cancel_confirm.html', {'pedido': pedido})


@login_required
def order_status_api(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    # Autoriza cliente dono ou restaurante dono
    if hasattr(request.user, 'cliente') and pedido.cliente == getattr(request.user, 'cliente', None):
        pass
    elif hasattr(request.user, 'restaurante') and pedido.restaurante == getattr(request.user, 'restaurante', None):
        pass
    else:
        return JsonResponse({'error': 'forbidden'}, status=403)
    return JsonResponse({
        'status': pedido.status,
        'status_display': pedido.get_status_display(),
    })


def cart_summary_api(request):
    count, total = _cart_summary(request.session)
    return JsonResponse({'count': count, 'total': str(total)})


@login_required
def confirm_received(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    # Apenas o cliente dono confirma recebimento
    if not hasattr(request.user, 'cliente') or pedido.cliente != request.user.cliente:
        return redirect('home')
    if request.method == 'POST':
        # Só permite confirmar quando está em trânsito
        if pedido.status == 'transito':
            pedido.status = 'entregue'
            pedido.save()
            messages.success(request, 'Pedido recebido! Bom apetite!')
        return redirect('order_tracking', pedido_id=pedido.id_pedido)
    # Se GET, redireciona para tracking
    return redirect('order_tracking', pedido_id=pedido.id_pedido)
