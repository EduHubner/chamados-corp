from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr

from app.models import PerfilEnum, PrioridadeEnum, StatusChamadoEnum, StatusTarefaEnum


# ---------- Usuário / Auth ----------

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: PerfilEnum = PerfilEnum.FUNCIONARIO
    departamento_id: Optional[str] = None


class UsuarioOut(BaseModel):
    id: str
    nome: str
    email: EmailStr
    perfil: PerfilEnum
    ativo: bool

    class Config:
        from_attributes = True


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    perfil: Optional[PerfilEnum] = None
    ativo: Optional[bool] = None
    departamento_id: Optional[str] = None
    nova_senha: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


# ---------- Chamado ----------

class ChamadoCreate(BaseModel):
    titulo: str
    descricao: str
    categoria_id: Optional[str] = None
    prioridade: PrioridadeEnum = PrioridadeEnum.MEDIA


class ChamadoUpdate(BaseModel):
    status: Optional[StatusChamadoEnum] = None
    responsavel_id: Optional[str] = None
    prioridade: Optional[PrioridadeEnum] = None
    descricao: Optional[str] = None


class ChamadoOut(BaseModel):
    id: str
    titulo: str
    descricao: str
    categoria_id: Optional[str] = None
    prioridade: PrioridadeEnum
    status: StatusChamadoEnum
    solicitante_id: str
    responsavel_id: Optional[str]
    data_abertura: datetime
    data_conclusao: Optional[datetime]

    class Config:
        from_attributes = True


# ---------- Comentário ----------

class ComentarioCreate(BaseModel):
    texto: str


class ComentarioOut(BaseModel):
    id: str
    texto: str
    autor_id: str
    criado_em: datetime

    class Config:
        from_attributes = True


# ---------- Tarefa ----------

class TarefaCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    responsavel_id: Optional[str] = None
    equipe_id: Optional[str] = None
    prazo: Optional[datetime] = None
    prioridade: PrioridadeEnum = PrioridadeEnum.MEDIA
    chamado_id: Optional[str] = None


class TarefaUpdate(BaseModel):
    status: Optional[StatusTarefaEnum] = None
    responsavel_id: Optional[str] = None
    prazo: Optional[datetime] = None


class TarefaOut(BaseModel):
    id: str
    titulo: str
    descricao: Optional[str]
    status: StatusTarefaEnum
    prioridade: PrioridadeEnum
    prazo: Optional[datetime]
    responsavel_id: Optional[str]

    class Config:
        from_attributes = True


# ---------- Dashboard ----------

class CategoriaCreate(BaseModel):
    nome: str


class DashboardOut(BaseModel):
    chamados_abertos: int
    chamados_concluidos: int
    chamados_em_atraso: int
    por_categoria: dict
    tempo_medio_resolucao_horas: Optional[float]
