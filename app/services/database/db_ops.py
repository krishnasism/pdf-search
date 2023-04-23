from .connectors import DatabaseConnection
from services.config import get_settings
from .databases import Databases
from datetime import datetime
from uuid import uuid4
import logging
import os

settings = get_settings()


def put_pdf_to_database(pdf_body, file_metadata):
    configured_db = settings.document_db_provider
    database_connection = DatabaseConnection(configured_db)
    match configured_db:
        case Databases.mongodb.value:
            return _put_pdf_body_mongodb(database_connection.db_client, pdf_body, file_metadata, database_name=settings.mongodb_db_name, table_name=settings.mongodb_collection_name)
        case Databases.aws.value:
            return _put_pdf_body_dynamodb(database_connection.db_client, pdf_body, file_metadata, table_name=settings.aws_search_table_name)
        case _:
            logging.error("[DB Ops - Document DB] Undefined provider")
            pass


def _put_pdf_body_dynamodb(dynamodb, pdfbody, metadata, table_name):
    try:
        table = dynamodb.Table(table_name)
        for page_num, page_data in pdfbody.items():
            table.put_item(Item={
                "pdf_body": str(page_data),
                "file_name":  f"{str(metadata.get('filename'))}_{str(uuid4().hex)}",
                "made_on": str(datetime.utcnow()),
                "page_num": str(page_num)
            })
    except Exception as e:
        logging.error(f"[DB Ops - DynamoDB] Error: {str(e)}")
        return False
    return True


def _put_pdf_body_mongodb(mongodb, pdfbody, metadata, database_name, table_name):
    try:
        db = mongodb[database_name]
        collection = db[table_name]
        for page_num, page_data in pdfbody.items():
            collection.insert_one({
                "pdf_body": str(page_data),
                "file_name":  f"{str(metadata.get('filename'))}_{str(uuid4().hex)}",
                "made_on": str(datetime.utcnow()),
                "page_num": str(page_num)
            })
    except Exception as e:
        logging.error(f"[DB Ops - MongoDB] Error: {str(e)}")
        return False
    return True
