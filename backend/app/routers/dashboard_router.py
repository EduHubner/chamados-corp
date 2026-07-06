from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=schemas.DashboardOut)
def obter_dashboard(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.exigir_perfil("gestor", "admin")),
):
    abertos = db.query(models.Chamado).filter(
        models.Chamado.status.in_([
            models.StatusChamadoEnum.ABERTO,
            models.StatusChamadoEnum.EM_ANDAMENTO,
            models.StatusChamadoEnum.AGUARDANDO_USUARIO,
        ])
    ).count()

    concluidos = db.query(models.Chamado).filter(
        models.Chamado.status.in_([
            models.StatusChamadoEnum.RESOLVIDO, models.StatusChamadoEnum.FECHADO
        ])
    ).count()

    # "Em atraso": chamados abertos há mais de 3 dias (regra simples, ajustável)
    em_atraso = db.query(models.Chamado).filter(
        models.Chamado.status.notin_([
            models.StatusChamadoEnum.RESOLVIDO, models.StatusChamadoEnum.FECHADO
        ]),
        func.age(datetime.utcnow(), models.Chamado.data_abertura) > "3 days",
    ).count()

    por_categoria_raw = (
        db.query(models.Categoria.nome, func.count(models.Chamado.id))
        .join(models.Chamado, models.Chamado.categoria_id == models.Categoria.id)
        .group_by(models.Categoria.nome)
        .all()
    )
    por_categoria = {nome: total for nome, total in por_categoria_raw}

    tempo_medio = db.query(
        func.avg(
            func.extract("epoch", models.Chamado.data_conclusao - models.Chamado.data_abertura)
        )
    ).filter(models.Chamado.data_conclusao.isnot(None)).scalar()

    tempo_medio_horas = round(tempo_medio / 3600, 2) if tempo_medio else None

    return schemas.DashboardOut(
        chamados_abertos=abertos,
        chamados_concluidos=concluidos,
        chamados_em_atraso=em_atraso,
        por_categoria=por_categoria,
        tempo_medio_resolucao_horas=tempo_medio_horas,
    )
