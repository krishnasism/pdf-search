import logging
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from tempfile import NamedTemporaryFile
from multiprocessing import Pool, Value, cpu_count
from itertools import chain
from api_helpers import update_document_progress
from services.utils.helpers import preprocess_parsed_text
from enums.FileStages import FileStages


class PDFParser:
    def __init__(self):
        logging.info("[PDF Parser] Initialised")

    def parse_pytesseract(self, page_chunk, document_progress):
        global counter
        start_page, chunk = page_chunk
        page_data = []
        for pageNum, imgBlob in enumerate(chunk):
            text = pytesseract.image_to_string(imgBlob, lang="eng")
            page_data.append((start_page + pageNum, preprocess_parsed_text(text)))
            with counter.get_lock():
                counter.value += 1
                if counter.value % 5 == 0:
                    document_progress["pages_parsed"] = 5
                    update_document_progress(document_progress)
        return page_data

    def get_ocr_body(self, path, document_progress: dict) -> str:
        global counter
        counter = Value("i", 0)
        body = {}
        pdf_info = pdfinfo_from_path(path)
        max_pages = pdf_info["Pages"]
        document_progress["pages_parsed"] = 0
        update_document_progress(document_progress)

        max_processes = cpu_count()
        pages_chunks = []
        chunk_size = min(max_pages, max(int(max_pages / max_processes), 1))

        for page in range(1, max_pages + 1, chunk_size):
            pages_chunks.append(
                (
                    page,
                    convert_from_path(
                        path, first_page=page, last_page=min(page + chunk_size - 1, max_pages)
                    ),
                )
            )
        with Pool(processes=5, initargs=(counter)) as pool:
            page_results = [
                pool.apply_async(
                    self.parse_pytesseract,
                    (
                        page_chunk,
                        document_progress,
                    ),
                )
                for page_chunk in pages_chunks
            ]
            pool.close()
            pool.join()
        multiple_results = list(
            chain(*[page_result.get() for page_result in page_results])
        )
        for result in multiple_results:
            body[result[0]] = result[1]

        # Prevent duplicate progress update for pages_parsed
        document_progress["pages_parsed"] = 0
        document_progress["stage"] = FileStages.COMPLETED.value
        update_document_progress(document_progress)

        return body

    def parse(self, path: str, document_progress: dict) -> str:
        """
        Parse PDF and get text from it
        params: path: Path to PDF file
        document_progress: Document progress
        return: body: Text from PDF
        """
        global counter
        counter = Value("i", 0)
        pdf_body = self.get_ocr_body(path, document_progress)
        return pdf_body


def get_pdf_body(
    pdf_file: NamedTemporaryFile,
    original_file_name: str,
    document_progress: dict,
) -> dict:
    """
    Parse PDF and get text from it
    params: pdf_file: PDF file
    original_file_name: Original file name
    document_progress: Document progress
    return: body: Text from PDF
    """
    file_metadata = {"filename": original_file_name}
    pdf_parser = PDFParser()

    body = pdf_parser.parse(pdf_file.name, document_progress)
    return body, file_metadata
