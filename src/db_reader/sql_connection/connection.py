from sqlalchemy import create_engine
import os
import logging
from llama_index.core import SQLDatabase
SERVER:str = os.getenv("IP")
USERNAME: str = os.getenv("USERNAME")
PASSWORD: str = os.getenv("PASSWORD")
DATABASE: str = os.getenv("DATABASE_NAME")
ENCODED_PASSWORD: str = os.getenv("ENCODED_PASSWORD")

connection_uri = f'mssql+pymssql://{USERNAME}:{ENCODED_PASSWORD}@{SERVER}/{DATABASE}'
engine = create_engine(connection_uri, pool_size=5, max_overflow=10)

sql_database = SQLDatabase(engine, include_tables=["Customer", "LMS_Loan_Master"])