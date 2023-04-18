from .connectors import StorageConnection
from .storage_providers import StorageProviders
import os
import tempfile
import requests
import traceback
from services.pdf.parsing.parser import get_pdf_body
from services.database.db_ops import put_pdf_to_database

from fastapi import UploadFile
import logging

def process_s3_files(bucket_name: str):
    storage_connection = StorageConnection(StorageProviders.aws.value)
    s3_client = storage_connection.storage_client
    bucket = s3_client.Bucket(bucket_name)
    try:
        for s3_object in bucket.objects.all():
            temp_file = tempfile.NamedTemporaryFile(mode='w+b')
            path, filename = os.path.split(s3_object.key)
            bucket.download_file(s3_object.key, temp_file.name)
            temp_file.close()
            file_metadata = {
                "filename": path + "/" + filename
            }
            pdf_body = get_pdf_body(UploadFile(
                open(temp_file.name, 'rb'), filename=filename))
        return True
    except Exception as e:
        logging.exception(e)
        return False