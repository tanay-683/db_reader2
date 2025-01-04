from db_reader.config.config import SettingConfigurationManager
from llama_index.core.query_engine import NLSQLTableQueryEngine
from db_reader.config.config import sql_connection
import logging
from ensure import ensure_annotations

    
setting_config_manager = SettingConfigurationManager()
print("part1")
settings = setting_config_manager.get_settings()
print("part2")
embed_model, llm = setting_config_manager.initialize_settings_config(settings)
print("part3")

TABLES = ["Customer", "LMS_Loan_Master"]
sql_database = sql_connection.get_sql_database(tables=TABLES)

class QueryEngine:
    
    def __init__(self):
        self.query_engine = None
    
    def get_query_engine(self) -> NLSQLTableQueryEngine:
        return NLSQLTableQueryEngine(
        sql_database=sql_database, 
        tables=TABLES,
        llm=llm, 
        embed_model=embed_model,
        sql_only=True,
        )
    @ensure_annotations
    def generate_sql_query(self, natural_language_query:str) -> str:
        try:
            if self.query_engine is None:
                logging.info(f"query_engine was NONE, setting it to NLSQLTableQueryEngine!!!")
                self.query_engine = self.get_query_engine()
                logging.info(f"query_engine set to NLSQLTableQueryEngine!!!")
            else:
                logging.info(f"query_engine was not NONE, setting it to NLSQLTableQueryEngine!!!")
                self.query_engine = self.query_engine
        except Exception as e:
            raise e
        response = self.query_engine.query(natural_language_query)
        
        logging.info("Query engine working fine!!!")
        sql_query = response.metadata["sql_query"]
        
        logging.info(f"\n\n\n Response: {response}\n\n\n")
        logging.info(f"\n\n\n SQL Query generated: {sql_query}\n\n\n")
        
        return str(sql_query)
