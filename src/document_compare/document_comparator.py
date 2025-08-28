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
from model.models import PromptType

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
        self.prompt = PROMPT_REGISTORY[PromptType.DOCUMENT_COMPARISON.value]
        self.chain = self.prompt | self.llm | self.fixing_parser
        self.log.info("DocumentComparatorLLM initialized successfully")
        
    
    def compare_documents(self, combined_document:str)-> pd.DataFrame:
        """
        Compare two documents and return the differences.
        """
        try:
            inputs={"combined_docs":combined_document,
                    "format_instruction":self.parser.get_format_instructions()}
            self.log.info("starting document comparison")
            response = self.chain.invoke(inputs)
            self.log.info("Document comparison completed successfully.",response_preview=str(response)[:200])
            return self._format_response(response)
        except Exception as e:
            self.log.error(f"Error comparing documents: {e}")
            raise DocumentPortalException("An error occurred while comparing documents.", sys)

    def _format_response(self,response:list[dict])-> pd.DataFrame:
        """
        Format the response from the language model to match the expected schema.
        """
        try:
            df = pd.DataFrame(response)
            self.log.info("Response formatted successfully.", records=len(df))
            return df
        except Exception as e:
            self.log.error(f"Error formatting response: {e}")
            raise DocumentPortalException("An error occurred while formatting the response.", sys)