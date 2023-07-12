from fastapi import APIRouter, UploadFile, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from typing import Annotated
from services.search.search import get_pdf_by_query
from services.storage.storage_ops import get_s3_presigned_url
from services.security.verify_token import verify_token
from services.queue.queue import prepare_job
from apis.requests.document_progress import DocumentProgressRequest
from enums.FileStages import FileStages
from services.local.postgres import PostgresManager

import logging

router = APIRouter()
token_auth_scheme = HTTPBearer()
pm = PostgresManager()


@router.get("/search")
async def pdf_search(
    query: str, user_email: str, authenticated: bool = Depends(verify_token)
):
    query = query.lower()
    response = get_pdf_by_query(query, user_email)

    documents = response.get("documents")
    error = response.get("error")

    return JSONResponse(
        content={
            "documents": documents if documents else None,
            "error": error if error else None,
        },
        status_code=200 if documents else 500,
    )


@router.post("/upload")
async def upload_pdf(
    file: UploadFile,
    summarize: Annotated[str, Form()],
    user_email: Annotated[str, Form()],
    store_files_in_cloud: Annotated[bool, Form()],
    store_in_elastic: Annotated[bool, Form()],
    store_in_document_db: Annotated[bool, Form()],
    bucket_name: Annotated[str, Form()],
    authenticated: bool = Depends(verify_token),
):
    return JSONResponse(content={"message": "Upload disabled in demo"}, status_code=201)
    try:
        job_metadata = prepare_job(
            file,
            params={
                "summarize": summarize,
                "user_email": user_email,
                "store_files_in_cloud": store_files_in_cloud,
                "store_in_elastic": store_in_elastic,
                "store_in_document_db": store_in_document_db,
                "bucket_name": bucket_name,
            },
        )
        document_id = job_metadata.get("document_id")
        total_pages = job_metadata.get("total_pages")

        pm.create_documents_progress_entry(
            DocumentProgressRequest(
                userEmail=user_email,
                documentId=document_id,
                documentName=file.filename,
                stage=FileStages.QUEUED.value,
                pagesParsed=0,
                totalPages=total_pages,
            ).model_dump()
        )

        return JSONResponse(content={"message": "Created"}, status_code=201)
    except Exception as e:
        logging.error(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/get-file-url")
async def get_file_url(
    bucket_name: str,
    file_name: str,
    user_email: str,
    authenticated: bool = Depends(verify_token),
):
    try:
        url = get_s3_presigned_url(bucket_name, file_name, user_email)

        return JSONResponse(
            content={"success": "true", "file_url": url}, status_code=200
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
