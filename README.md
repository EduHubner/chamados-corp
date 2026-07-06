# Sistema de Gerenciamento de Chamados e Atividades Corporativas

Projeto desenvolvido para a disciplina de Infraestrutura e Serviços Web, com arquitetura baseada em nuvem (Application Load Balancer, instâncias EC2 com containers Docker, banco de dados RDS PostgreSQL com réplica, armazenamento S3 e monitoramento via CloudWatch).

## Stack utilizada

Backend em Python com FastAPI, SQLAlchemy e PostgreSQL. Frontend em React (Vite). Autenticação via JWT, com quatro perfis de usuário: funcionário, técnico, gestor e admin. Armazenamento de anexos em Amazon S3 através do SDK boto3.

## Funcionalidades principais

Abertura, acompanhamento e encerramento de chamados, com categorização, prioridade e histórico de comentários. Gestão de tarefas e subtarefas vinculadas a equipes. Painel administrativo para cadastro e gerenciamento de usuários (perfis, ativação/desativação). Cadastro de categorias por gestores e administradores. Upload e consulta de anexos por chamado. Dashboard gerencial com indicadores de chamados abertos, concluídos, em atraso, tempo médio de resolução e distribuição por categoria.

## Perfis e permissões

| Perfil | Permissões principais |
|---|---|
| Funcionário | Abrir chamados, consultar os próprios chamados, comentar e anexar arquivos |
| Técnico | Receber e atualizar chamados, editar descrição, excluir chamados, gerenciar tarefas |
| Gestor | Visualizar dashboard, distribuir atividades, cadastrar categorias |
| Admin | Todas as permissões acima, além de cadastro e gerenciamento de usuários |

## Estrutura do projeto

```
backend/    API FastAPI (modelos, rotas, autenticação)
frontend/   Aplicação React
docker-compose.yml   Orquestração dos serviços para ambiente local
```

## Execução local

Pré-requisito: Docker e Docker Compose.

```bash
docker compose up --build
```

API disponível em `http://localhost:8000/docs` (documentação Swagger gerada automaticamente pelo FastAPI). Frontend disponível em `http://localhost:5173`.

Criação do primeiro usuário do sistema, via requisição HTTP (o campo perfil enviado é ignorado pelo endpoint público, que sempre cria como funcionário):

```bash
curl -X POST http://localhost:8000/auth/registrar \
  -H "Content-Type: application/json" \
  -d '{"nome":"Admin","email":"admin@empresa.com","senha":"123456"}'
```

Para que esse primeiro usuário tenha acesso ao painel administrativo, o campo perfil precisa ser alterado manualmente para admin diretamente no banco de dados (tabela usuarios), já que a rota que permite definir perfis livremente (`/admin/usuarios`) exige autenticação como admin. Essa etapa manual é necessária apenas para o primeiro usuário administrador; os demais usuários podem ser cadastrados normalmente pelo painel.

Sem uma conta AWS configurada, o upload de anexos não é concluído, pois depende do Amazon S3. As demais funcionalidades operam normalmente em ambiente local.

## Infraestrutura em nuvem

A documentação da arquitetura de implantação na AWS Academy Learner Lab está descrita em `AWS_DEPLOY_GUIDE.md`.