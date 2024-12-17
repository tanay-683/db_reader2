import fireducks.pandas as pd
import logging
import re
import datetime
from ensure import ensure_annotations



class ChunkCleaningPipeline:
    def __init__(self, chunk:pd.DataFrame):
        self.chunk = chunk
        self.columns = self.chunk.columns
    
    
    @ensure_annotations
    def remove_unnecessary_columns(self):
        col_to_remove:list = []
        for col in self.columns:
            if re.search(pattern="Is|Id", string=col):
                col_to_remove.append(col)
            elif re.search(pattern="create|modify", string=col, flags=re.IGNORECASE):
                col_to_remove.append(col)
        self.chunk.drop(columns=col_to_remove, inplace=True)
        return self
    
    
    @ensure_annotations
    def prune_columns_with_high_null_percentage(self):
        # removing columns which contain 85% none values
        threshold: float = 0.85
        self.chunk = self.chunk.loc[:, self.chunk.isnull().mean() <= threshold]
 
        
        return self


    @ensure_annotations
    def downcasting_dataframe_datatypes(self):
        
        # connverting int64 to int16
        int64_columns = self.chunk.select_dtypes(include=["int64"]).columns # select columns with int64 datatype
        self.chunk[int64_columns] = self.chunk[int64_columns].astype("int16")

        # Identify columns with float64 data type and convert to float16
        float64_columns = self.chunk.select_dtypes(include=["float64"]).columns
        self.chunk[float64_columns] = self.chunk[float64_columns].astype("float32")
        return self
    
    
    @ensure_annotations
    def format_data_and_datetime_to_string(self):
        for col in self.chunk.columns:
            if self.chunk[col].dtype == 'datetime64[ns]':
                self.chunk[col] = self.chunk[col].dt.strftime('%Y-%m-%d')
            elif self.chunk[col].dtype == 'object':
                self.chunk[col] = self.chunk[col].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime.date) else x)
        return self    
        
        
    def convert_chunk_to_dictionary(self):
        self.chunk = self.chunk.where(pd.notnull(self.chunk), None).to_dict(orient='records')
        return self
    
    def nan_to_none(self):
        self.chunk = [{k: None if v != v else v for k, v in row.items()} for row in self.chunk]
        return self
    
    
    def execute(self):
        return self.chunk