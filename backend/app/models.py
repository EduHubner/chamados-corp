import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, Enum, Boolean, Table
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


# ---------- ENUMS ----------

class PerfilEnum(str, enum.Enum):
    FUNCIONARIO = "funcionario"
    TECNICO = "tecnico"
    GESTOR = "gestor"
    ADMIN = "admin"


class PrioridadeEnum(str, enum.Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class StatusChamadoEnum(str, enum.Enum):
    ABERTO = "aberto"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO_USUARIO = "aguardando_usuario"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"


class StatusTarefaEnum(str, enum.Enum):
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    ATRASADA = "atrasada"


# ---------- TABELA ASSOCIATIVA equipe <-> usuario ----------

equipe_membros = Table(
    "equipe_membros",
    Base.metadata,
    Column("equipe_id", UUID(as_uuid=False), ForeignKey("equipes.id"), primary_key=True),
    Column("usuario_id", UUID(as_uuid=False), ForeignKey("usuarios.id"), primary_key=True),
)


# ---------- ENTIDADES ----------

class Departamento(Base):
    __tablename__ = "departamentos"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nome = Column(String(120), nullable=False, unique=True)

    usuarios = relationship("Usuario", back_populates="departamento")


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(Enum(PerfilEnum), nullable=False, default=PerfilEnum.FUNCIONARIO)
    ativo = Column(Boolean, default=True)
    departamento_id = Column(UUID(as_uuid=False), ForeignKey("departamentos.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    departamento = relationship("Departamento", back_populates="usuarios")
    chamados_abertos = relationship("Chamado", foreign_keys="Chamado.solicitante_id", back_populates="solicitante")
    chamados_responsavel = relationship("Chamado", foreign_keys="Chamado.responsavel_id", back_populates="responsavel")
    equipes = relationship("Equipe", secondary=equipe_membros, back_populates="membros")


class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nome = Column(String(120), nullable=False, unique=True)

    chamados = relationship("Chamado", back_populates="categoria")


class Equipe(Base):
    __tablename__ = "equipes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    nome = Column(String(120), nullable=False, unique=True)

    membros = relationship("Usuario", secondary=equipe_membros, back_populates="equipes")
    tarefas = relationship("Tarefa", back_populates="equipe")


class Chamado(Base):
    __tablename__ = "chamados"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=False)
    categoria_id = Column(UUID(as_uuid=False), ForeignKey("categorias.id"), nullable=True)
    prioridade = Column(Enum(PrioridadeEnum), nullable=False, default=PrioridadeEnum.MEDIA)
    status = Column(Enum(StatusChamadoEnum), nullable=False, default=StatusChamadoEnum.ABERTO)
    solicitante_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=False)
    responsavel_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=True)
    data_abertura = Column(DateTime, default=datetime.utcnow)
    data_conclusao = Column(DateTime, nullable=True)

    categoria = relationship("Categoria", back_populates="chamados")
    solicitante = relationship("Usuario", foreign_keys=[solicitante_id], back_populates="chamados_abertos")
    responsavel = relationship("Usuario", foreign_keys=[responsavel_id], back_populates="chamados_responsavel")
    comentarios = relationship("Comentario", back_populates="chamado", cascade="all, delete-orphan")
    anexos = relationship("Anexo", back_populates="chamado", cascade="all, delete-orphan")


class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    responsavel_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=True)
    equipe_id = Column(UUID(as_uuid=False), ForeignKey("equipes.id"), nullable=True)
    prazo = Column(DateTime, nullable=True)
    prioridade = Column(Enum(PrioridadeEnum), nullable=False, default=PrioridadeEnum.MEDIA)
    status = Column(Enum(StatusTarefaEnum), nullable=False, default=StatusTarefaEnum.PENDENTE)
    chamado_id = Column(UUID(as_uuid=False), ForeignKey("chamados.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    responsavel = relationship("Usuario")
    equipe = relationship("Equipe", back_populates="tarefas")
    subtarefas = relationship("Subtarefa", back_populates="tarefa", cascade="all, delete-orphan")


class Subtarefa(Base):
    __tablename__ = "subtarefas"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    tarefa_id = Column(UUID(as_uuid=False), ForeignKey("tarefas.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    concluida = Column(Boolean, default=False)

    tarefa = relationship("Tarefa", back_populates="subtarefas")


class Comentario(Base):
    __tablename__ = "comentarios"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    chamado_id = Column(UUID(as_uuid=False), ForeignKey("chamados.id"), nullable=False)
    autor_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=False)
    texto = Column(Text, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    chamado = relationship("Chamado", back_populates="comentarios")
    autor = relationship("Usuario")


class Anexo(Base):
    __tablename__ = "anexos"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    chamado_id = Column(UUID(as_uuid=False), ForeignKey("chamados.id"), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)
    enviado_por_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    chamado = relationship("Chamado", back_populates="anexos")


class Notificacao(Base):
    __tablename__ = "notificacoes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    usuario_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=False)
    mensagem = Column(String(500), nullable=False)
    lida = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario")


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    usuario_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=True)
    acao = Column(String(255), nullable=False)
    entidade = Column(String(100), nullable=False)
    entidade_id = Column(String(100), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
