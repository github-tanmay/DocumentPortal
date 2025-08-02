
from Exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from Prompt.prompt_library import prompt

from model.models import Metadata

class DocumentAnalyzer:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(
                self.parser,
                self.llm,
            )

            self.prompt = prompt

            self.log.info("DocumentAnalyzer initialized successfully")

        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPortalException("Error initializing DocumentAnalyzer", e) from e
        
    
    def analyze_document(self, document_text: str) -> dict:
        """
        Analyze the document using the LLM and return structured metadata
        """
        try:
            chain = self.prompt | self.llm | self.fixing_parser

            self.log.info("Meta-data analysis chain is initialized")

            response = chain.invoke({
                "document_text": document_text,
                "format_instructions": self.parser.get_format_instructions()
            })

            self.log.info("Document analyzed successfully", keys =list(response.keys()))
            return response

        except Exception as e:
            self.log.error(f"Error analyzing document: {e}")
            raise DocumentPortalException("Error analyzing document", e) from e


    
    