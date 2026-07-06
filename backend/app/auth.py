from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def criar_token(usuario_id: str, perfil: str) -> str:
    expira = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": usuario_id, "perfil": perfil, "exp": expira}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def get_usuario_atual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise credenciais_invalidas
    except JWTError:
        raise credenciais_invalidas

    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas
    return usuario


def exigir_perfil(*perfis: str):
    """Dependência que restringe o acesso a determinados perfis (ex.: gestor, admin)."""
    def checador(usuario: models.Usuario = Depends(get_usuario_atual)):
        if usuario.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para executar esta ação",
            )
        return usuario
    return checador
