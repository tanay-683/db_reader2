import logging
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.query_engine import NLSQLTableQueryEngine
import llama_index.core.llms
from dataclasses import dataclass
from typing import Optional
from llama_index.core import Settings

from src.db_reader.model.model import get_gemini_model
from src.db_reader.sql_connection.connection import SqlConnection
from llama_index.llms.gemini import Gemini


TABLES = ["Customer", "LMS_Loan_Master"]
sql_connection = SqlConnection()
engine = sql_connection.get_engine()
sql_database = sql_connection.get_sql_database(tables=TABLES)

CHUNK_SIZE = 20

@dataclass
class SettingConfig:
    embed_model: Optional[HuggingFaceEmbedding] = None
    llm: Optional[llama_index.core.llms.LLM] = None
    
    
class SettingConfigurationManager:
    def __init__(self):
        self.setting_config = SettingConfig()
        
    def get_settings(self)-> SettingConfig:
        try:
            if self.setting_config.embed_model is None:
                logging.info(f"embed_model was NONE, setting it to {HuggingFaceEmbedding}!!!")
                self.setting_config.embed_model = HuggingFaceEmbedding(model_name= "sentence-transformers/all-mpnet-base-v2")
                logging.info(f"embed_model set to {HuggingFaceEmbedding}!!!")
            else:
                logging.info(f"embed_model was not NONE, setting it to HuggingFaceEmbedding!!!")
                self.setting_config.embed_model = self.setting_config.embed_model
                
                
            if self.setting_config.llm is None:
                logging.info(f"llm was NONE, setting it to {get_gemini_model()}!!!")
                self.setting_config.llm = get_gemini_model()
                logging.info(f"llm set to Gemini!!!")
            else:
                logging.info(f"llm was not NONE, setting it to {self.setting_config.llm}!!!")
                self.setting_config.llm = self.setting_config.llm
            
            return self.setting_config
        except Exception as e:
            logging.error(f"Error in getting settings: {e}")
            raise    
    

    def initialize_settings_config(self,setting_config: SettingConfig):
        try:
            setting_config = self.get_settings()
            embed_model = setting_config.embed_model
            llm = setting_config.llm
            return embed_model, llm
        except Exception as e:
            logging.error(f"Error in initializing settings: {e}")
            raise

         
        
setting_config_manager = SettingConfigurationManager()
print("part1")
settings = setting_config_manager.get_settings()
print("part2")
embed_model, llm = setting_config_manager.initialize_settings_config(settings)
print("part3")

class QueryEngine:
    
    def get_query_engine(self):
        return NLSQLTableQueryEngine(
        sql_database=sql_database, 
        tables=TABLES,
        llm=llm, 
        embed_model=embed_model,
        sql_only=True,
        verbose=True
        )
        
    def generate_sql_query(self, natural_language_query:str):
        query_engine = self.get_query_engine()
        response = query_engine.query(natural_language_query)
        sql_query = response.metadata["sql_query"]
        print("\n\n\n Response: ", response,"\n\n\n")
        return sql_query
