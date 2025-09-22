from datetime import datetime, time
from sqlalchemy import select
from app.extensions import db
from app.models.restaurant import HorarioFuncionamentoRestaurante


def aberto_agora(restaurante_id: int, now: datetime | None = None) -> bool:
    now = now or datetime.now()
    weekday_map = {
        0: "Segunda",
        1: "Terça",
        2: "Quarta",
        3: "Quinta",
        4: "Sexta",
        5: "Sábado",
        6: "Domingo",
    }
    dia_nome = weekday_map[now.weekday()]

    stmt = select(HorarioFuncionamentoRestaurante).where(
        HorarioFuncionamentoRestaurante.restaurante_id == restaurante_id,
        HorarioFuncionamentoRestaurante.dia_semana == dia_nome,
    )
    horario = db.session.execute(stmt).scalars().first()
    if not horario:
        return False

    inicio: time = horario.horario_abertura
    fim: time = horario.horario_fechamento
    agora_t: time = now.time()

    if inicio <= fim:
        return inicio <= agora_t <= fim
    # janela virando o dia (ex.: 18:00–02:00)
    return agora_t >= inicio or agora_t <= fim

