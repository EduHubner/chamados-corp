from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(tags=["Cadastros"])


@router.get("/usuarios", response_model=List[schemas.UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.exigir_perfil("gestor", "admin", "tecnico")),
):
    return db.query(models.Usuario).all()


@router.get("/categorias")
def listar_categorias(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    return [{"id": c.id, "nome": c.nome} for c in db.query(models.Categoria).order_by(models.Categoria.nome).all()]


@router.post("/categorias")
def criar_categoria(
    dados: schemas.CategoriaCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.exigir_perfil("gestor", "admin")),
):
    existente = db.query(models.Categoria).filter(models.Categoria.nome == dados.nome).first()
    if existente:
        raise HTTPException(status_code=400, detail="Já existe uma categoria com esse nome")
    cat = models.Categoria(nome=dados.nome)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"id": cat.id, "nome": cat.nome}


@router.get("/equipes")
def listar_equipes(db: Session = Depends(get_db)):
    return [{"id": e.id, "nome": e.nome} for e in db.query(models.Equipe).all()]
