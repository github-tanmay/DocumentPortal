import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from utils.config_loader import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from logger.custom_logger import CustomLogger
from Exception.custom_exception import DocumentPortalException

log = CustomLogger().get_logger(__file__)

class ModelLoader:
    """ 
    Utility class to load models based on configuration
    
    """
    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        log.info("Configuration loaded successfully", config_key = list(self.config.keys()))


    def _validate_env(self):
        """ Validate required environment variables """
        required_vars =["GROQ_API_KEY","GOOGLE_API_KEY"]
        self.api_keys = {key: os.getenv(key) for key in required_vars }
        missing = [key for key, value in self.api_keys.items() if not value]
        if missing:
            log.error(f"Missing environment variable", missing_vars=missing)
            raise DocumentPortalException(f"Missing environment variables", sys)

    def load_embedding(self):
        """
        Load the embedding model based on configurtion"""
        try:
            log.info("loading embedding model ..")
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model=model_name)
        except Exception as e:
            log.error("Failed to load embedding model",error=str(e))
            raise DocumentPortalException(f"Failed to load embedding model", sys)
        
    def load_llm(self):
        """
        Load the LLM model based on configuration"""

        llm_block = self.config["llm"]

        log.info("loading the llm model ...")

        provider_key = os.getenv("groq", "groq")
        if provider_key not in llm_block:
            log.error(f"Provider {provider_key} not found in configuration", provider=provider_key)
            raise ValueError(f"Provider {provider_key} not found in configuration")

        llm_config = llm_block[provider_key]
        provider  =llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_tokens", 2048)

        log.info("Loading LLM", provider=provider, model=model_name, temperature=temperature, max_tokens=max_tokens)

        if provider == "groq":
            llm = ChatGroq(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.api_keys["GROQ_API_KEY"]
            )
            return llm
        
        elif provider == "google":
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            return llm

        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")
        

if __name__ == "__main__":
    loader = ModelLoader()

    embedding = loader.load_embedding()

    result = embedding.embed_query("hello, how are you? ")
    print("Embedding result:", result)

    llm = loader.load_llm()
    response = llm.invoke("What is the capital of France?")
    print("LLM response:", response.content)