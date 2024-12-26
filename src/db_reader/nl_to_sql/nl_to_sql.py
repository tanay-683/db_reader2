from db_reader.config.config import *
from db_reader.config.config import query_engine

def generate_sql_query(natural_language_query:str):
    response = query_engine.query(natural_language_query)
    sql_query = response.metadata["sql_query"]
    return sql_query
    