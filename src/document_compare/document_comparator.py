import os
from dotenv import load_dotenv
import sys
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from model.models import ChangeFormat
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from Prompt.prompt_library import PROMPT_REGISTORY
from exception.custom_exception import DocumentPortalException

class DocumentComparatorLLM:
    """
    A class to handle document comparison using a language model.
    """
    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser(pydantic_object=ChangeFormat)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTORY["document_comparsion"]
        self.chain = self.prompt | self.llm | self.fixing_parser
        self.log.info("DocumentComparatorLLM initialized successfully")
        
    
    def compare_documents(self, document1, document2):
        """
        Compare two documents and return the differences.
        """
        pass

    def _format_response(self):
        """
        Format the response from the language model to match the expected schema.
        """
        pass