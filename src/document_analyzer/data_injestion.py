import os
import sys
from Exception.custom_exception import DocumentPortalException
from dotenv import load_dotenv
from datetime import datetime
import uuid
from langchain_community.document_loaders import PyPDFLoader
from logger.custom_logger import CustomLogger


class DocumentHandler:
    """
    Utility class to analyze documents based on configuration
    """
    def __init__(self,data_dir=None,session_id=None):
        try:
            self.log=CustomLogger().get_logger(__name__)
            self.data_dir = data_dir or os.getenv(
                "DATA_STORAGE_PATH",
                os.path.join(os.getcwd(), "data", "document_analysis")
            )
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create base session directory
            self.session_path = os.path.join(self.data_dir, self.session_id)
            
            os.makedirs(self.session_path, exist_ok=True)

            self.log.info("PDFHandler initialized", session_id=self.session_id, session_path=self.session_path)

        except Exception as e:
            self.log.error(f"Error initializing DocumentHandler: {e}")
            raise DocumentPortalException("Error initializing DocumentHandler", e) from e

    def save_pdf(self,uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)

            if not filename.lower().endswith('.pdf'):
                raise DocumentPortalException("Invalid file type. Only PDF files are allowed.")
            
            save_path = os.path.join(self.session_path,filename)

            with open(save_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            self.log.info("PDF saved successfully", filename=filename, save_path=save_path, session_id=self.session_id)
            return save_path


        except Exception as e:
            self.log.error(f"Error saving PDF: {e}")
            raise DocumentPortalException("Error saving PDF", e) from e

    def read_pdf(self,pdf_path):
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            self.log.info("PDF read successfully", pdf_path=pdf_path, document_count=len(documents))
            return documents
        except Exception as e:
            self.log.error(f"Error reading PDF: {e}")
            raise DocumentPortalException("Error reading PDF", e) from e


# if __name__ == "__main__":
#     from pathlib import Path
#     from io import BytesIO
    
#     pdf_path=r"C:\\Users\Asus\\OneDrive\\Desktop\\TanmayFiles\\Project1\\DocumentPortal\\data\\NIPS-2017-attention-is-all-you-need-Paper.pdf"
#     class DummnyFile:
#         def __init__(self,file_path):
#             self.name = Path(file_path).name
#             self._file_path = file_path
#         def getbuffer(self):
#             return open(self._file_path, "rb").read()
        
#     dummy_pdf = DummnyFile(pdf_path)
    
#     handler = DocumentHandler()
    
#     try:
#         saved_path=handler.save_pdf(dummy_pdf)
#         print(saved_path)
        
#         content=handler.read_pdf(saved_path)
#         print("PDF Content:")
#         print(content[:50])  # Print first 500 characters of the PDF content
        
#     except Exception as e:
#         print(f"Error: {e}")