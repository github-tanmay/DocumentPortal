from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
import sys
from datetime import datetime
import uuid
import os

class DocumentInjestion:
    """
    Handles the ingestion of documents, specifically PDF files.
    Provides functionality to save and read PDF files.
    """
    def __init__(self,base_dir:str = "data/document_compare",session_id=None):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        
        self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
       # Create base session directory
        self.session_path = self.base_dir/self.session_id
        self.session_path.mkdir(parents =True, exist_ok=True)

        self.log.info("Document comparator", session_id=self.session_id, session_path=self.session_path)

    def save_uploaded_file(self,ref_fileName,actual_fileName):
        """ Saves an uploaded file to the upload directory.
        """
        try:
            ref_Path=self.session_path/ref_fileName.name
            actual_Path=self.session_path/actual_fileName.name

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
                        all_text.append(f"\n --- page {page_num + 1} --- \n{text}")
                self.log.info("PDF file read successfully.",file = str(pdf_path),pages = len(all_text))
                return "\n".join(all_text)
        except Exception as e:
            self.log.error(f"Error reading PDF file: {e}")
            raise DocumentPortalException("An error occurred while reading the PDF file.",sys)
        
    def combine_documents(self)-> str:
        """
        Combines the text of two documents for comparison.
        """
        try:
            content_dict= {}
            doc_parts = []

            for filename in sorted(self.session_path.iterdir()):
                if filename.is_file() and filename.suffix == '.pdf':
                    content_dict[filename.name]= self.read_pdf(filename)

            for filename, content in content_dict.items():
                doc_parts.append(f"Document: {filename}\n{content}")

            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined successfully.", count=len(doc_parts))
            return combined_text
        except Exception as e:
            self.log.error(f"Error combining documents: {e}")
            raise DocumentPortalException("An error occurred while combining the documents.", sys)
        
    def clean_old_session(self,keep_latest:int = 5):
        """
        Cleans up old session directories, keeping only the latest specified number of sessions.
        """
        try:
            all_sessions = sorted([d for d in self.base_dir.iterdir() if d.is_dir()], reverse=True)
            old_sessions = all_sessions[keep_latest:]

            for session in old_sessions:
                for item in session.iterdir():
                    if item.is_file():
                        item.unlink()
                session.rmdir()
                self.log.info("Old session cleaned up.", session=str(session))

        except Exception as e:
            self.log.error(f"Error cleaning old sessions: {e}")
            raise DocumentPortalException("An error occurred while cleaning old sessions.", sys)