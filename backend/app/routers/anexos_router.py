import uuid

import boto3
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import models, auth
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/chamados/{chamado_id}/anexos", tags=["Anexos"])


def get_s3_client():
    # Em EC2 na AWS Academy Lab, o boto3 usa automaticamente as credenciais
    # do LabInstanceProfile associado à instância — não é preciso configurar
    # access key/secret aqui.
    return boto3.client("s3", region_name=settings.aws_region)


@router.post("")
def upload_anexo(
    chamado_id: str,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    chamado = db.query(models.Chamado).filter(models.Chamado.id == chamado_id).first()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")

    extensao = arquivo.filename.split(".")[-1] if "." in arquivo.filename else "bin"
    s3_key = f"chamados/{chamado_id}/{uuid.uuid4()}.{extensao}"

    try:
        s3 = get_s3_client()
        s3.upload_fileobj(arquivo.file, settings.aws_s3_bucket, s3_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao enviar para o S3: {e}")

    anexo = models.Anexo(
        chamado_id=chamado_id,
        nome_arquivo=arquivo.filename,
        s3_key=s3_key,
        enviado_por_id=usuario.id,
    )
    db.add(anexo)
    db.commit()
    db.refresh(anexo)
    return {"id": anexo.id, "nome_arquivo": anexo.nome_arquivo, "s3_key": anexo.s3_key}


@router.get("")
def listar_anexos(
    chamado_id: str,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(auth.get_usuario_atual),
):
    anexos = db.query(models.Anexo).filter(models.Anexo.chamado_id == chamado_id).all()
    s3 = get_s3_client()
    resultado = []
    for a in anexos:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.aws_s3_bucket, "Key": a.s3_key},
            ExpiresIn=3600,
        )
        resultado.append({"id": a.id, "nome_arquivo": a.nome_arquivo, "url": url})
    return resultado
