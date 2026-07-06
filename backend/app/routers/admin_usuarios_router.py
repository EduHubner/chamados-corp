from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/admin/usuarios", tags=["Administração de Usuários"])


@router.get("", response_model=List[schemas.UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.exigir_perfil("admin")),
):
    return db.query(models.Usuario).order_by(models.Usuario.nome).all()


@router.post("", response_model=schemas.UsuarioOut)
def criar_usuario(
    dados: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.exigir_perfil("admin")),
):
    """Admin pode criar usuário com qualquer perfil (funcionário, técnico,
    gestor ou admin) — diferente do /auth/registrar, que é público e
    sempre cria como funcionário."""
    if db.query(models.Usuario).filter(models.Usuario.email == dados.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    novo = models.Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=auth.hash_senha(dados.senha),
        perfil=dados.perfil,
        departamento_id=dados.departamento_id,
    )
    db.add(novo)
    db.add(models.LogAuditoria(
        usuario_id=usuario.id, acao="criou_usuario", entidade="usuario", entidade_id=None
    ))
    db.commit()
    db.refresh(novo)
    return novo


@router.patch("/{usuario_id}", response_model=schemas.UsuarioOut)
def atualizar_usuario(
    usuario_id: str,
    dados: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_admin: models.Usuario = Depends(auth.exigir_perfil("admin")),
):
    alvo = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if alvo.id == usuario_admin.id and dados.ativo is False:
        raise HTTPException(status_code=400, detail="Você não pode desativar a si mesmo")
    if alvo.id == usuario_admin.id and dados.perfil is not None and dados.perfil != models.PerfilEnum.ADMIN:
        raise HTTPException(status_code=400, detail="Você não pode remover seu próprio perfil de admin")

    if dados.nome is not None:
        alvo.nome = dados.nome
    if dados.perfil is not None:
        alvo.perfil = dados.perfil
    if dados.ativo is not None:
        alvo.ativo = dados.ativo
    if dados.departamento_id is not None:
        alvo.departamento_id = dados.departamento_id
    if dados.nova_senha:
        alvo.senha_hash = auth.hash_senha(dados.nova_senha)

    db.add(models.LogAuditoria(
        usuario_id=usuario_admin.id, acao="atualizou_usuario", entidade="usuario", entidade_id=alvo.id
    ))
    db.commit()
    db.refresh(alvo)
    return alvo
