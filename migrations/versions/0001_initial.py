"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-09-22

"""
from alembic import op
import sqlalchemy as sa


revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    tipo_usuario = sa.Enum('CLIENTE', 'RESTAURANTE_OWNER', name='tipo_usuario', native_enum=False)
    dia_semana = sa.Enum('Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo', name='dia_semana', native_enum=False)
    status_pedido = sa.Enum('preparacao','transito','entregue','cancelado', name='status_pedido', native_enum=False)

    op.create_table(
        'usuarios',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('nome_completo', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('telefone', sa.Text(), nullable=False),
        sa.Column('senha_hash', sa.Text(), nullable=False),
        sa.Column('tipo', tipo_usuario, nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)

    op.create_table(
        'categorias_pratos',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('nome_categoria', sa.Text(), nullable=False, unique=True),
    )

    op.create_table(
        'restaurantes',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('owner_id', sa.BigInteger(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('nome', sa.Text(), nullable=False),
        sa.Column('endereco', sa.Text(), nullable=False),
        sa.Column('telefone', sa.Text(), nullable=False),
        sa.Column('tipo_culinaria', sa.Text(), nullable=False),
        sa.Column('nota_media', sa.Numeric(2,1), server_default='0', nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.CheckConstraint('nota_media >= 0 AND nota_media <= 5', name='ck_restaurantes_nota'),
    )
    op.create_index('ix_restaurantes_nome', 'restaurantes', ['nome'])
    op.create_index('ix_restaurantes_tipo', 'restaurantes', ['tipo_culinaria'])

    op.create_table(
        'horarios_funcionamento_restaurantes',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('restaurante_id', sa.BigInteger(), sa.ForeignKey('restaurantes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dia_semana', dia_semana, nullable=False),
        sa.Column('horario_abertura', sa.Time(), nullable=False),
        sa.Column('horario_fechamento', sa.Time(), nullable=False),
        sa.UniqueConstraint('restaurante_id','dia_semana', name='uq_restaurante_dia'),
    )

    op.create_table(
        'enderecos_cliente',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('cliente_id', sa.BigInteger(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
        sa.Column('apelido', sa.Text(), nullable=True),
        sa.Column('logradouro', sa.Text(), nullable=False),
        sa.Column('numero', sa.Text(), nullable=False),
        sa.Column('bairro', sa.Text(), nullable=False),
        sa.Column('cidade', sa.Text(), nullable=False),
        sa.Column('uf', sa.Text(), nullable=False),
        sa.Column('cep', sa.Text(), nullable=False),
        sa.Column('complemento', sa.Text(), nullable=True),
        sa.UniqueConstraint('cliente_id','apelido', name='uq_cliente_apelido'),
    )

    op.create_table(
        'pratos',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('restaurante_id', sa.BigInteger(), sa.ForeignKey('restaurantes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('categoria_id', sa.BigInteger(), sa.ForeignKey('categorias_pratos.id'), nullable=False),
        sa.Column('nome', sa.Text(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=False),
        sa.Column('preco', sa.Numeric(10,2), nullable=False),
        sa.Column('disponivel', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('estoque', sa.Integer(), server_default='0', nullable=False),
        sa.CheckConstraint('preco >= 0', name='ck_pratos_preco_pos'),
        sa.CheckConstraint('estoque >= 0', name='ck_pratos_estoque_pos'),
    )
    op.create_index('ix_pratos_rest_cat_disp', 'pratos', ['restaurante_id','categoria_id','disponivel'])

    op.create_table(
        'avaliacoes_restaurantes',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('restaurante_id', sa.BigInteger(), sa.ForeignKey('restaurantes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cliente_id', sa.BigInteger(), sa.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True),
        sa.Column('nota', sa.Integer(), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.CheckConstraint('nota >= 0 AND nota <= 5', name='ck_avaliacao_nota_range'),
    )

    op.create_table(
        'pedidos',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('cliente_id', sa.BigInteger(), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('restaurante_id', sa.BigInteger(), sa.ForeignKey('restaurantes.id'), nullable=False),
        sa.Column('endereco_entrega_id', sa.BigInteger(), sa.ForeignKey('enderecos_cliente.id'), nullable=False),
        sa.Column('status', status_pedido, server_default='preparacao', nullable=False),
        sa.Column('forma_pagamento', sa.Text(), nullable=False),
        sa.Column('valor_subtotal', sa.Numeric(10,2), nullable=False),
        sa.Column('taxa_empresa', sa.Numeric(10,2), nullable=False),
        sa.Column('valor_total', sa.Numeric(10,2), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'itens_pedido',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('pedido_id', sa.BigInteger(), sa.ForeignKey('pedidos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('prato_id', sa.BigInteger(), sa.ForeignKey('pratos.id'), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=False),
        sa.Column('preco_unitario', sa.Numeric(10,2), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.CheckConstraint('quantidade >= 1', name='ck_itens_qtde_pos'),
    )


def downgrade() -> None:
    op.drop_table('itens_pedido')
    op.drop_table('pedidos')
    op.drop_table('avaliacoes_restaurantes')
    op.drop_index('ix_pratos_rest_cat_disp', table_name='pratos')
    op.drop_table('pratos')
    op.drop_table('enderecos_cliente')
    op.drop_table('horarios_funcionamento_restaurantes')
    op.drop_index('ix_restaurantes_tipo', table_name='restaurantes')
    op.drop_index('ix_restaurantes_nome', table_name='restaurantes')
    op.drop_table('restaurantes')
    op.drop_table('categorias_pratos')
    op.drop_index('ix_usuarios_email', table_name='usuarios')
    op.drop_table('usuarios')

