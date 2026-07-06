from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/chamados", tags=["Chamados"])


def _registrar_log(db: Session, usuario_id: str, acao: str, entidade_id: str):
    db.add(models.LogAuditoria(
        usuario_id=usuario_id, acao=acao, entidade="chamado", entidade_id=entidade_id
    ))


@router.post("", response_model=schemas.ChamadoOut)
def criar_chamado(
    dados: schemas.ChamadoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    chamado = models.Chamado(
        titulo=dados.titulo,
        descricao=dados.descricao,
        categoria_id=dados.categoria_id,
        prioridade=dados.prioridade,
        solicitante_id=usuario.id,
    )
    db.add(chamado)
    db.flush()
    _registrar_log(db, usuario.id, "criou_chamado", chamado.id)
    db.commit()
    db.refresh(chamado)
    return chamado


@router.get("", response_model=List[schemas.ChamadoOut])
def listar_chamados(
    status: Optional[models.StatusChamadoEnum] = None,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    query = db.query(models.Chamado)
    # Funcionário só vê os próprios chamados; técnico/gestor/admin veem todos
    if usuario.perfil == models.PerfilEnum.FUNCIONARIO:
        query = query.filter(models.Chamado.solicitante_id == usuario.id)
    if status:
        query = query.filter(models.Chamado.status == status)
    return query.order_by(models.Chamado.data_abertura.desc()).all()


@router.get("/{chamado_id}", response_model=schemas.ChamadoOut)
def obter_chamado(
    chamado_id: str,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    chamado = db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    if usuario.perfil == models.PerfilEnum.FUNCIONARIO and chamado.solicitante_id != usuario.id:
        raise HTTPException(status_code=403, detail="Sem permissão para ver este chamado")
    return chamado


@router.patch("/{chamado_id}", response_model=schemas.ChamadoOut)
def atualizar_chamado(
    chamado_id: str,
    dados: schemas.ChamadoUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.exigir_perfil("tecnico", "gestor", "admin")),
):
    chamado = db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    if dados.status is not None:
        chamado.status = dados.status
        if dados.status in (models.StatusChamadoEnum.RESOLVIDO, models.StatusChamadoEnum.FECHADO):
            chamado.data_conclusao = datetime.utcnow()
    if dados.responsavel_id is not None:
        chamado.responsavel_id = dados.responsavel_id
    if dados.prioridade is not None:
        chamado.prioridade = dados.prioridade
    if dados.descricao is not None:
        if usuario.perfil not in (models.PerfilEnum.TECNICO, models.PerfilEnum.ADMIN):
            raise HTTPException(
                status_code=403,
                detail="Somente técnico ou admin podem editar a descrição do chamado",
            )
        chamado.descricao = dados.descricao

    _registrar_log(db, usuario.id, "atualizou_chamado", chamado.id)
    db.commit()
    db.refresh(chamado)
    return chamado


@router.delete("/{chamado_id}", status_code=204)
def excluir_chamado(
    chamado_id: str,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.exigir_perfil("tecnico", "admin")),
):
    chamado = db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    # Comentários e anexos (registros no banco) são removidos em cascata.
    # Observação: os arquivos correspondentes no S3 não são apagados
    # automaticamente aqui — se quiser, dá para estender chamando o
    # s3.delete_object para cada anexo antes do db.delete().
    db.add(models.LogAuditoria(
        usuario_id=usuario.id, acao="excluiu_chamado", entidade="chamado", entidade_id=chamado.id
    ))
    db.delete(chamado)
    db.commit()
    return None


@router.post("/{chamado_id}/comentarios", response_model=schemas.ComentarioOut)
def comentar(
    chamado_id: str,
    dados: schemas.ComentarioCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    chamado = db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    comentario = models.Comentario(chamado_id=chamado_id, autor_id=usuario.id, texto=dados.texto)
    db.add(comentario)
    db.commit()
    db.refresh(comentario)
    return comentario


@router.get("/{chamado_id}/comentarios", response_model=List[schemas.ComentarioOut])
def listar_comentarios(
    chamado_id: str,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    return (
        db.query(models.Comentario)
        .filter(models.Comentario.chamado_id == chamado_id)
        .order_by(models.Comentario.criado_em)
        .all()
    )
