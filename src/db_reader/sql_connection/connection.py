from sqlalchemy import create_engine, text
import os, sys
import logging
from llama_index.core import SQLDatabase
from dataclasses import dataclass


@dataclass
class SqlConnetionConfig:
    CONNECTION_URI: str

class SqlConnection:
    def __init__(self):
        pass
    
    def get_engine(self):
        '''
        Returns a connection engine object
        '''
        connection_config = SqlConnetionConfig(
            CONNECTION_URI = f"""mssql+pymssql://{os.getenv("USERNAME")}:{os.getenv("ENCODED_PASSWORD")}@{os.getenv("IP")}/{os.getenv("DATABASE_NAME")}"""
            )
        
        engine = create_engine(connection_config.CONNECTION_URI, pool_size=5, max_overflow=10)
        
        try:
            with engine.connect() as con:
                rows = con.execute(text("""SELECT 1"""))
                for row in rows:
                    if sys.getsizeof(row) != 0:
                        logging.info("Connection established")
            return engine
        except:
            logging.error("Failed to establish connection with database!!!")
            
            
    def get_sql_database(self, tables:list[str]):
        '''
        Returns a SQLDatabase object
        '''
        return SQLDatabase(self.get_engine(), include_tables=tables)
    