from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


@router.post("", response_model=schemas.TarefaOut)
def criar_tarefa(
    dados: schemas.TarefaCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.exigir_perfil("tecnico", "gestor", "admin")),
):
    tarefa = models.Tarefa(**dados.model_dump())
    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.get("", response_model=List[schemas.TarefaOut])
def listar_tarefas(
    responsavel_id: Optional[str] = None,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    query = db.query(models.Tarefa)
    if usuario.perfil == models.PerfilEnum.TECNICO:
        query = query.filter(models.Tarefa.responsavel_id == usuario.id)
    if responsavel_id:
        query = query.filter(models.Tarefa.responsavel_id == responsavel_id)
    return query.order_by(models.Tarefa.criado_em.desc()).all()


@router.patch("/{tarefa_id}", response_model=schemas.TarefaOut)
def atualizar_tarefa(
    tarefa_id: str,
    dados: schemas.TarefaUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    tarefa = db.query(models.Tarefa).filter(models.Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    if usuario.perfil == models.PerfilEnum.TECNICO and tarefa.responsavel_id != usuario.id:
        raise HTTPException(status_code=403, detail="Sem permissão")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(tarefa, campo, valor)

    db.commit()
    db.refresh(tarefa)
    return tarefa


@router.post("/{tarefa_id}/subtarefas")
def criar_subtarefa(
    tarefa_id: str,
    titulo: str,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    sub = models.Subtarefa(tarefa_id=tarefa_id, titulo=titulo)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"id": sub.id, "titulo": sub.titulo, "concluida": sub.concluida}
