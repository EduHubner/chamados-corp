# Guia de Deploy — AWS Academy Learner Lab

Este guia segue exatamente o seu diagrama: Usuários → Internet → Application
Load Balancer → Camada de Aplicação (2x EC2 com Docker) → Camada de Dados
(RDS Principal + Réplica) + S3 (arquivos) + CloudWatch (monitoramento).

## 0. Particularidades do AWS Academy Learner Lab (leia antes de tudo)

O Lab é diferente de uma conta AWS normal, e isso muda como você trabalha:

- **Não existe criação de roles IAM.** Você não pode criar uma role nova.
  Use sempre a role já pronta chamada **`LabRole`** (e o instance profile
  **`LabInstanceProfile`**) ao criar EC2, RDS, etc. É essa role que dá
  permissão para a EC2 acessar o S3 automaticamente (sem precisar colocar
  access key/secret no código).
- **A sessão expira** (geralmente ~4h, ou quando você clica em "End Lab").
  Quando isso acontece, os recursos podem ser desligados/perdidos, e as
  credenciais temporárias mudam. **Anote seus passos** (ou automatize com
  scripts) para não ter que redescobrir tudo na próxima sessão.
- **Região:** o Lab normalmente já vem fixado em `us-east-1` (N. Virginia).
  Confira no canto superior direito do console.
- **Sem conta de billing/orçamento próprios** — os limites já vêm definidos
  pelo curso.

Recomendo: primeiro deixe tudo funcionando manualmente pelo Console (para
entender e printar/documentar no relatório), depois — se sobrar tempo —
migre para o AWS CLI/Terraform.

---

## 1. VPC e Sub-redes

Use a **VPC padrão (default)** da conta — ela já vem com sub-redes públicas
em pelo menos 2 Availability Zones, o que é suficiente para o ALB e o RDS
Multi-AZ.

`VPC > Your VPCs` → confirme que existe uma `default`. Anote o VPC ID.

---

## 2. Security Groups (regras de firewall)

Crie 3 Security Groups (`EC2 > Security Groups > Create`):

| Nome | Regras de entrada (Inbound) |
|---|---|
| `sg-alb` | HTTP (80) de `0.0.0.0/0` |
| `sg-app` | HTTP (8000) e HTTP (80) — origem: `sg-alb` (não 0.0.0.0/0!) |
| `sg-rds` | PostgreSQL (5432) — origem: `sg-app` |

Isso reproduz o fluxo do diagrama: só a internet fala com o ALB, só o ALB
fala com as EC2, só as EC2 falam com o banco.

---

## 3. Banco de Dados — Amazon RDS (Camada de Dados)

`RDS > Create database`:

- Engine: **PostgreSQL**
- Modelo: **Multi-AZ DB instance** (isso já cria automaticamente a réplica
  síncrona em standby — é o "Amazon RDS Réplica de Leitura/Standby" do seu
  diagrama, com failover automático = Alta Disponibilidade)
- Classe: `db.t3.micro` (elegível ao free tier / suficiente para o lab)
- Usuário mestre: `postgres` / defina uma senha
- VPC: a default | Security Group: `sg-rds`
- Nome do banco inicial: `chamados`
- **Anote o endpoint** gerado (algo como
  `chamados.xxxxx.us-east-1.rds.amazonaws.com`)

> Se quiser uma réplica de leitura assíncrona separada (além do Multi-AZ),
> dá pra criar depois em `Actions > Create read replica`. Para o projeto de
> disciplina, o Multi-AZ já demonstra o conceito de replicação/HA do
> diagrama.

---

## 4. Armazenamento de Arquivos — Amazon S3

`S3 > Create bucket`:

- Nome único globalmente, ex.: `chamados-corp-anexos-eduardo123`
- Região: `us-east-1`
- Bloqueie acesso público (deixe o padrão marcado) — o backend usa
  **presigned URLs** para servir os arquivos com segurança, então não
  precisa deixar o bucket público.

Atualize o nome do bucket na variável de ambiente `AWS_S3_BUCKET` do backend
(passo 6).

---

## 5. Application Load Balancer (Balanceamento de Carga)

`EC2 > Load Balancers > Create > Application Load Balancer`:

- Scheme: **internet-facing**
- Listener: HTTP 80
- Sub-redes: selecione pelo menos 2 AZs da VPC default
- Security group: `sg-alb`
- Target group: crie um **Target group** tipo "Instances", protocolo HTTP,
  porta **8000** (a porta do backend FastAPI/uvicorn), com health check no
  caminho **`/health`** (já implementado na API)

Depois anote o **DNS name** do ALB — será o endereço público da aplicação.

> Dica para o relatório: esse ALB é o que aparece como "Application Load
> Balancer / Distribui as requisições" no seu diagrama.

---

## 6. Camada de Aplicação — 2x EC2 com Docker

Crie **2 instâncias EC2** idênticas (para bater com o diagrama):

`EC2 > Launch Instance`:

- AMI: **Amazon Linux 2023**
- Tipo: `t2.micro` ou `t3.micro`
- **IAM Instance Profile: `LabInstanceProfile`** — isso é o que dá acesso
  ao S3 sem precisar de access key/secret hardcoded
- Security group: `sg-app`
- **User data** (script de inicialização automática — cole em "Advanced
  details > User data"):

```bash
#!/bin/bash
dnf update -y
dnf install -y docker git
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

# Clona seu repositório (suba o projeto no GitHub antes)
git clone https://github.com/SEU_USUARIO/chamados-corp.git /home/ec2-user/app
cd /home/ec2-user/app/backend

docker build -t chamados-backend .
docker run -d --name backend --restart unless-stopped -p 8000:8000 \
  -e DATABASE_URL="postgresql://postgres:SUASENHA@SEU-ENDPOINT-RDS.rds.amazonaws.com:5432/chamados" \
  -e SECRET_KEY="troque-esta-chave" \
  -e AWS_S3_BUCKET="chamados-corp-anexos-eduardo123" \
  -e AWS_REGION="us-east-1" \
  -e FRONTEND_ORIGIN="*" \
  chamados-backend
```

Repita para a segunda instância (mesmo script). Depois, registre as duas
instâncias no **Target Group** do ALB (`EC2 > Target Groups > seu grupo >
Register targets`).

> Alternativa mais simples se preferir não usar `git clone`: envie os
> arquivos do backend via `scp` para a instância antes de rodar o Docker.

### Frontend

O jeito mais simples para o lab: rode o frontend **em uma das mesmas EC2**
(ou uma terceira), também via Docker, apontando `VITE_API_URL` para o DNS
do ALB:

```bash
cd /home/ec2-user/app/frontend
docker build --build-arg VITE_API_URL=http://SEU-DNS-DO-ALB -t chamados-frontend .
docker run -d --name frontend --restart unless-stopped -p 80:80 chamados-frontend
```

(Isso exige adicionar `ARG VITE_API_URL` e `ENV VITE_API_URL` no Dockerfile
do frontend antes do `RUN npm run build` — posso ajustar isso pra você se
for esse o caminho que escolher.)

---

## 7. Monitoramento — Amazon CloudWatch

Já vem habilitado por padrão para métricas básicas (CPU, rede) de EC2 e
RDS. Para deixar mais completo pro seu diagrama:

- `CloudWatch > Dashboards > Create dashboard` — monte um painel com:
  CPUUtilization das EC2, conexões do RDS (`DatabaseConnections`),
  requisições do ALB (`RequestCount`, `HTTPCode_Target_5XX_Count`)
- `CloudWatch > Alarms > Create alarm` — crie um alarme simples de CPU alta
  (>80%) em uma das EC2, só para demonstrar o conceito no relatório
- (Opcional, avançado) Instalar o **CloudWatch Agent** nas EC2 para enviar
  logs do container Docker para **CloudWatch Logs**

---

## 8. Testando tudo

1. Acesse `http://SEU-DNS-DO-ALB/health` → deve responder `{"status":"ok"}`
2. Acesse `http://SEU-DNS-DO-ALB/docs` → Swagger da API
3. Acesse o frontend pelo IP público/DNS da instância e faça login

---

## 9. Checklist final para o relatório/apresentação

- [ ] Print do diagrama de arquitetura (você já tem)
- [ ] Print do RDS mostrando Multi-AZ ativo (Alta Disponibilidade)
- [ ] Print do Target Group do ALB com as 2 instâncias "healthy"
- [ ] Print do bucket S3 com um anexo de teste enviado
- [ ] Print do dashboard do CloudWatch
- [ ] Demonstração funcional: login → abrir chamado → anexar arquivo →
      técnico muda status → gestor vê no dashboard

---

## Dúvidas comuns

**"A instância EC2 não consegue conectar no RDS."**
Confira se o Security Group `sg-rds` libera a porta 5432 tendo como origem
o `sg-app` (não um IP fixo).

**"Erro de permissão no S3 mesmo com LabInstanceProfile."**
Confirme que a instância foi lançada JÁ com o instance profile associado
(não dá para adicionar depois em todos os casos do Lab — mais fácil recriar
a instância).

**"Perdi tudo quando a sessão do Lab expirou."**
É esperado — o Learner Lab não é uma conta persistente. Documente os passos
(ou os comandos de user data) para conseguir recriar rapidamente na próxima
sessão. Se possível, exporte os dados do RDS (`pg_dump`) antes de encerrar.
