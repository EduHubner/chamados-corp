from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registrar", response_model=schemas.UsuarioOut)
def registrar(dados: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Auto-cadastro público. Sempre cria como 'funcionario' — a criação de
    técnicos, gestores e admins é feita pelo painel de administração
    (/admin/usuarios), restrito a usuários com perfil admin."""
    if db.query(models.Usuario).filter(models.Usuario.email == dados.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    usuario = models.Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=auth.hash_senha(dados.senha),
        perfil=models.PerfilEnum.FUNCIONARIO,
        departamento_id=dados.departamento_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=schemas.Token)
def login(dados: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == dados.email).first()
    if not usuario or not auth.verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos"
        )
    token = auth.criar_token(usuario.id, usuario.perfil.value)
    return schemas.Token(access_token=token, usuario=usuario)


@router.get("/me", response_model=schemas.UsuarioOut)
def me(usuario: models.Usuario = Depends(auth.get_usuario_atual)):
    return usuario
