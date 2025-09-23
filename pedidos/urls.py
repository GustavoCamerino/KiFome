from django.urls import path
from .views import (
    add_to_cart, view_cart, remove_from_cart,
    checkout, order_tracking, advance_status,
    buy_now, cancel_order, order_status_api, cart_summary_api,
    confirm_received
)

urlpatterns = [
    path('carrinho/', view_cart, name='view_cart'),
    path('carrinho/add/<int:prato_id>/', add_to_cart, name='add_to_cart'),
    path('carrinho/remove/<int:prato_id>/', remove_from_cart, name='remove_from_cart'),
    path('carrinho/summary/', cart_summary_api, name='cart_summary_api'),
    path('checkout/', checkout, name='checkout'),
    path('comprar/<int:prato_id>/', buy_now, name='buy_now'),
    path('pedido/<int:pedido_id>/', order_tracking, name='order_tracking'),
    path('pedido/<int:pedido_id>/avancar/', advance_status, name='advance_status'),
    path('pedido/<int:pedido_id>/cancelar/', cancel_order, name='cancel_order'),
    path('pedido/<int:pedido_id>/recebido/', confirm_received, name='confirm_received'),
    path('pedido/<int:pedido_id>/status/', order_status_api, name='order_status_api'),
]
