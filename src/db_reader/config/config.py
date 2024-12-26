from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import logging
from llama_index.core.query_engine import NLSQLTableQueryEngine

from db_reader.model.model import get_gemini_model
from db_reader.sql_connection.connection import sql_database

Settings.embed_model = HuggingFaceEmbedding(model_name= "sentence-transformers/all-mpnet-base-v2")
logging.info("Loading HuggingFace embedding model!!")
logging.info("HuggingFace embedding model loaded!!")
Settings.llm = get_gemini_model()
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=["Customer", "LMS_Loan_Master"], llm=Settings.llm)
