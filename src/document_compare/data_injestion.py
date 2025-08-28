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
    def __init__(self,base_dir):
        self.log = CustomLogger.get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    
    def delete_existing_files(self):
        """ Deletes all existing files in the upload directory.
        """
        try:
           if self.base_dir.exists() and self.base_dir.is_dir():
               for file in self.base_dir.iterdir():
                   if file.is_file():
                       file.unlink()
               self.log.info("Existing files deleted successfully.",directory = str(self.base_dir))
        except Exception as e:
            self.log.error(f"Error deleting existing files: {e}")
            raise DocumentPortalException("An error occurred while deleting existing files.", sys)

    def save_uploaded_file(self,ref_fileName,actual_fileName):
        """ Saves an uploaded file to the upload directory.
        """
        try:
            self.delete_existing_files()
            self.log.info("Existing files deleted successfully.")

            ref_Path=self.base_dir/ref_fileName.name
            actual_Path=self.base_dir/actual_fileName.name

            if not ref_fileName.name.endswith('.pdf') and not actual_fileName.name.endswith('.pdf'):
                self.log.error("Only Pdf file is allowed.")
                raise ValueError("Only Pdf file is allowed.")
            
            with open(ref_Path,"wb")  as f:
                f.write(ref_fileName.getbuffer())
            
            with open(actual_Path,"wb")  as f:
                f.write(actual_fileName.getbuffer())

            self.log.info("File saved successfully.", reference= str(ref_Path), actual=str(actual_Path))
            return ref_Path,actual_Path
        
        except Exception as e:
            self.log.error(f"Error saving uploaded file: {e}")
            raise DocumentPortalException("An error occurred while saving the uploaded file.", sys)

    def read_pdf(self, pdf_path:Path)-> str:
        """
        Reads a PDF file and extracts its text content.
        """
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    self.log.error("The PDF file is encrypted and cannot be read.")
                    raise ValueError("The PDF file is encrypted and cannot be encrypted: {pdf_path.name}")
                all_text =[]
                for page_num in range(doc.page_count):
                    page= doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        all.text.append(f"\n --- page {page_num + 1} --- \n{text}")
                self.log.info("PDF file read successfully.",file = str(pdf_path),pages = len(all_text))
                return "\n".join(all_text)
        except Exception as e:
            self.log.error(f"Error reading PDF file: {e}")
            raise DocumentPortalException("An error occurred while reading the PDF file.",sys)