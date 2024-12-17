from flask import Flask, render_template, Response, request, redirect, url_for
import logging
import pandas as pd
import json
import sys
import time
import gc
import datetime

from src.db_reader.preprocessing.preprocess import ChunkCleaningPipeline
from src.db_reader.sql_connection.connection import engine



app = Flask(__name__)


gen_query = "SELECT 1"


@app.route('/', methods=["GET", 'POST'])
def login():
    if request.method == "POST":
        return redirect(url_for(chat))  
    return render_template('login.html')


@app.route("/chat", methods=["GET", 'POST'])
def chat(): 
    
    return render_template('home_page.html')

@app.route('/load_data')
def load_data():
    def generate():
        try:
            has_columns_sent = False
            start_time = time.time()
            # Use chunking to retrieve data
            
            #########################################
            chunk_size = 20
            #########################################
            
            query = gen_query
            # Track total rows processed
            total_rows_processed = 0
            # Use chunking parameter in read_sql
            for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
                
                # Convert date and datetime objects to strings
                for col in chunk.columns:
                    if chunk[col].dtype == 'datetime64[ns]':
                        chunk[col] = chunk[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                    elif chunk[col].dtype == 'object':
                        chunk[col] = chunk[col].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime.date) else x)
                        
                # =============================
                pipeline = ChunkCleaningPipeline(chunk)
                chunk = list(pipeline
                                .remove_unnecessary_columns()
                                .prune_columns_with_high_null_percentage()
                                .downcasting_dataframe_datatypes()
                                .format_data_and_datetime_to_string()
                                .convert_chunk_to_dictionary()
                                .nan_to_none()
                                .execute()
                                )
                
                # =============================
                
                
                total_rows_processed += len(chunk)
                # Yield each chunk as JSON
                if not has_columns_sent:
                    yield json.dumps({
                        'rows': chunk,
                        'columns': pd.DataFrame(chunk).columns.tolist(),
                        'total_processed': total_rows_processed
                    }) + '\n'
                    has_columns_sent = True
                else:
                    yield json.dumps({
                        'rows': chunk,
                        'total_processed': total_rows_processed
                    }) + '\n'
                
                print("="*60)
                print(f"TOTAL ROWS SENT :-: {total_rows_processed}")
                print(f"time taken :-: {time.time() - start_time}")
                print(f"Columns Before Preprocessing :-:{pd.DataFrame(chunk).shape} \n {pd.DataFrame(chunk).columns}")
                print(f"Columns After Preprocessing :-:{pd.DataFrame(chunk).shape} \n {pd.DataFrame(chunk).columns}")
                
                print("="*60)
        except Exception as e:
            logging.error(f"Error in data generation: {e}")
            yield json.dumps({"error": str(e)})
    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
    