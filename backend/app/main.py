from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import (
    auth_router, chamados_router, tarefas_router, anexos_router,
    dashboard_router, cadastros_router, admin_usuarios_router,
)

# Cria as tabelas automaticamente (em produção, prefira Alembic para migrações)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gerenciamento de Chamados e Atividades Corporativas",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(chamados_router.router)
app.include_router(tarefas_router.router)
app.include_router(anexos_router.router)
app.include_router(dashboard_router.router)
app.include_router(cadastros_router.router)
app.include_router(admin_usuarios_router.router)


@app.get("/health")
def health():
    """Usado pelo Application Load Balancer (health check) e monitoramento."""
    return {"status": "ok"}


@app.get("/")
def raiz():
    return {"mensagem": "API do Sistema de Gerenciamento de Chamados e Atividades Corporativas"}
