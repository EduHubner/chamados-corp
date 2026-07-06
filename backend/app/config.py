from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Banco de dados (RDS PostgreSQL em produção, container local em dev)
    database_url: str = "postgresql://postgres:postgres@db:5432/chamados"

    # JWT
    secret_key: str = "troque-esta-chave-em-producao"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8  # 8 horas

    # AWS S3 (armazenamento de anexos)
    aws_s3_bucket: str = "chamados-corp-anexos"
    aws_region: str = "us-east-1"
    # Em produção na AWS Academy Lab, as credenciais vêm do IAM Instance
    # Profile da EC2 (LabInstanceProfile) — não é necessário colocar aqui.
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None

    # CORS
    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
