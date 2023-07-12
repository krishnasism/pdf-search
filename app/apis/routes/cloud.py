from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from services.local.postgres import PostgresManager
from services.security.verify_token import verify_token
from services.storage.storage_ops import get_all_s3_files
from services.queue.queue import prepare_s3_job
from apis.requests.document_progress import DocumentProgressRequest
from enums.FileStages import FileStages
from typing import Annotated

import logging


router = APIRouter()

pm = PostgresManager()


@router.get("/all-bucket-files")
async def update_settings(
    bucket_name: str, user_email: str, authenticated: bool = Depends(verify_token)
):
    s3_response = get_all_s3_files(bucket_name, user_email)
    return JSONResponse(
        content={
            "s3_response": s3_response,
        },
        status_code=200,
    )


@router.post("/s3-parsing-job")
async def s3_parsing_job(
    source_bucket_name: Annotated[str, Form()],
    key_name: Annotated[str, Form()],
    user_email: Annotated[str, Form()],
    viewer_bucket_name: Annotated[str, Form()],
    authenticated: bool = Depends(verify_token),
):
    return JSONResponse(content={"message": "Upload disabled in demo"}, status_code=201)
    try:
        document_id = await prepare_s3_job(
            source_bucket_name,
            key_name,
            user_email,
            viewer_bucket_name,
        )

        pm.create_documents_progress_entry(
            DocumentProgressRequest(
                userEmail=user_email,
                documentId=document_id,
                documentName=key_name,
                stage=FileStages.QUEUED.value,
                pagesParsed=0,
                totalPages=0,
            ).model_dump()
        )

        return JSONResponse(content={"message": "Created"}, status_code=201)
    except Exception as e:
        logging.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
