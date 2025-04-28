import logging
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
import llama_index.core.llms
from dataclasses import dataclass, field
from typing import Optional

from db_reader.model.model import get_gemini_model, get_ollama_model
from db_reader.sql_connection.connection import SqlConnection
from ensure import ensure_annotations
from typing import Tuple, Union
import os


CHUNK_SIZE = 20

# =======================================

sql_connection = SqlConnection()
engine = sql_connection.get_engine()

# =======================================

@dataclass
class SettingConfig:
    model_name = "models/embedding-001"
    embed_model = GeminiEmbedding(model_name=model_name, api_key=os.getenv("GOOGLE_API_KEY"))
    
    embed_model: Optional[GeminiEmbedding] = field(default_factory=lambda: GeminiEmbedding(model_name="models/embedding-001", api_key=os.getenv("GOOGLE_API_KEY")))
    llm: Optional[llama_index.core.llms.LLM] = field(default_factory=get_gemini_model)

    def __post_init__(self):
        logging.info("SettingConfig initialized with embed_model: %s", self.embed_model)
        logging.info("SettingConfig initialized with llm: %s", self.llm)
    
class SettingConfigurationManager:
    def __init__(self):
        self.setting_config = SettingConfig()   
        
    @ensure_annotations
    def get_settings(self)-> SettingConfig:
        try:
            if self.setting_config.embed_model is None:
                logging.info(f"embed_model was NONE, setting it to HuggingFaceEmbedding!!!")
                self.setting_config.embed_model = HuggingFaceEmbedding(model_name= "sentence-transformers/all-mpnet-base-v2")
                logging.info(f"embed_model set to HuggingFaceEmbedding!!!")
            else:
                logging.info(f"embed_model was not NONE, set to HuggingFaceEmbedding!!!")
                self.setting_config.embed_model = self.setting_config.embed_model
                
                
            if self.setting_config.llm is None:
                logging.info(f"llm was NONE, setting it to {get_gemini_model()}!!!")
                # self.setting_config.llm = get_gemini_model()
                self.setting_config.llm = get_ollama_model()
                logging.info(f"llm set to Gemini!!!")
            else:
                logging.info(f"llm was not NONE, set to self.setting_config.llm!!!")
                self.setting_config.llm = self.setting_config.llm
            
            return self.setting_config
        except Exception as e:
            logging.error(f"Error in getting settings: {e}")
            raise    
    

    def initialize_settings_config(self,setting_config: SettingConfig) -> Union[Tuple[HuggingFaceEmbedding, llama_index.core.llms.LLM]]:
        try:
            logging.info(f"Initializing settings config!!!")
            setting_config = self.get_settings()
            embed_model = setting_config.embed_model
            llm = setting_config.llm
            return embed_model, llm
        except Exception as e:
            logging.error(f"Error in initializing settings: {e}")
            raise
