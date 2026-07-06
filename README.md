# Sistema de Gerenciamento de Chamados e Atividades Corporativas

Projeto da disciplina de Infraestrutura e Serviços Web — arquitetura pensada
para rodar na AWS (ALB → EC2/Docker → RDS PostgreSQL + S3 + CloudWatch),
igual ao diagrama do projeto.

## Stack

- **Backend:** Python + FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** React (Vite)
- **Anexos:** Amazon S3 (via boto3)
- **Autenticação:** JWT (perfis: funcionário, técnico, gestor, admin)

## Rodando localmente (antes de ir para a AWS)

Pré-requisito: Docker e Docker Compose instalados.

```bash
docker compose up --build
```

- Backend (API): http://localhost:8000/docs (Swagger, já vem pronto no FastAPI)
- Frontend: http://localhost:5173

### Criando o primeiro usuário (gestor/admin)

Use o Swagger em `/docs` ou curl:

```bash
curl -X POST http://localhost:8000/auth/registrar \
  -H "Content-Type: application/json" \
  -d '{"nome":"Admin","email":"admin@empresa.com","senha":"123456","perfil":"admin"}'
```

Depois faça login pelo frontend com esse e-mail/senha.

> Sem uma conta AWS configurada, o upload de anexos (S3) vai falhar — isso é
> esperado em ambiente local puro. O resto do sistema funciona normalmente.

## Próximo passo

Veja `AWS_DEPLOY_GUIDE.md` para o passo a passo de deploy na AWS Academy
Learner Lab, replicando a arquitetura do diagrama (ALB, EC2 com Docker, RDS
com réplica, S3, CloudWatch).
