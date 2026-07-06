# Infraestrutura AWS

Documentação da arquitetura de implantação do sistema na AWS Academy Learner Lab, correspondente ao diagrama do projeto (Usuários, Internet, Application Load Balancer, Camada de Aplicação, Camada de Dados, Armazenamento de Arquivos e Monitoramento).

## Particularidades do ambiente

O AWS Academy Learner Lab difere de uma conta AWS convencional. Não há criação de roles IAM; os recursos que exigem permissões (como acesso da EC2 ao S3) utilizam a role já disponibilizada pela plataforma, `LabRole`, associada às instâncias através do instance profile `LabInstanceProfile`. As sessões possuem duração limitada e, ao expirar, os recursos criados podem ser desligados ou perdidos. A região utilizada é `us-east-1`.

## Rede

Utiliza a VPC padrão da conta, com sub-redes já distribuídas em múltiplas zonas de disponibilidade, suficiente para suportar o Application Load Balancer e o RDS Multi-AZ.

### Security Groups

| Grupo | Origem permitida | Porta |
|---|---|---|
| sg-alb | 0.0.0.0/0 | 80 |
| sg-app | sg-alb | 8000 e 80 |
| sg-rds | sg-app | 5432 |

O tráfego segue o fluxo do diagrama: a internet acessa apenas o load balancer, o load balancer acessa apenas as instâncias de aplicação, e o banco de dados aceita conexões apenas das instâncias de aplicação.

## Camada de dados (Amazon RDS)

Instância PostgreSQL configurada como Multi-AZ, o que corresponde ao par "Banco Principal / Réplica de Leitura-Standby" do diagrama, com replicação síncrona e failover automático em caso de falha na instância principal. Classe `db.t3.micro`, adequada aos limites do ambiente de laboratório.

## Armazenamento de arquivos (Amazon S3)

Bucket dedicado ao armazenamento de anexos dos chamados. O acesso público ao bucket permanece bloqueado; os arquivos são servidos por meio de URLs pré-assinadas geradas pelo backend, com validade limitada.

## Balanceamento de carga (Application Load Balancer)

Load balancer do tipo internet-facing, listener HTTP na porta 80, distribuindo requisições para um target group com as instâncias da camada de aplicação, na porta 8000. O health check utiliza o endpoint `/health` exposto pela API.

## Camada de aplicação (Amazon EC2)

Duas instâncias EC2 (Amazon Linux), cada uma executando o backend em container Docker, registradas no target group do load balancer. O instance profile `LabInstanceProfile` concede às instâncias acesso ao bucket S3 sem necessidade de credenciais fixas no código.

## Monitoramento (Amazon CloudWatch)

Métricas padrão de CPU, rede e conexões de banco de dados, complementadas por um dashboard consolidando indicadores das instâncias EC2, do RDS e do ALB, além de alarme de utilização de CPU.

## Limitações conhecidas

Os objetos armazenados no S3 não são removidos automaticamente quando um chamado é excluído no sistema. A atualização de código nas instâncias EC2 não é automatizada, dependendo de reconstrução manual do container a cada alteração.