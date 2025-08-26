from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
import sys

class DocumentInjestion:
    """
    Handles the ingestion of documents, specifically PDF files.
    Provides functionality to save and read PDF files.
    """
    def __init__(self):
        self.log = CustomLogger.get_logger(__name__)

    
    def delete_existing_files(self):
        pass

    def save_uploaded_file(self):
        pass
    def read_pdf(self, pdf_path:Path)-> str:
        """
        Reads a PDF file and extracts its text content.
        """
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    self.log.error("The PDF file is encrypted and cannot be read.")
                    raise ValueError("The PDF file is encrypted: {pdf_path.name}")
                all_text =[]
                for page_num in range(doc.page_count):
                    page= doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        all.text.append(f"\n --- page {page_num + 1} --- \n{text}")
                    self.log.info("PDF file read successfully.",file = str(pdf_path),pages = len(pdf_path))
        except Exception as e:
            self.log.error(f"Error reading PDF file: {e}")
            raise DocumentPortalException("An error occurred while reading the PDF file.",sys)