from flask import Flask, request, render_template, jsonify, Response
import logging
from src.db_reader.sql_connection.connection import engine
import pandas as pd
import json,sys
import time
import gc
import datetime

app = Flask(__name__)


gen_query = "SELECT * FROM Acc_Voucher_Details"

@app.route('/')
def login():
    return render_template('login.html')

@app.route("/chat", methods=["GET", 'POST'])
def chat():
    try:
        start_time = time.time()
        
        # # Fetch columns first
        columns_query = gen_query
        columns_df = pd.read_sql(columns_query, engine)

        columns = columns_df.columns.tolist()
        
        # deleting the df
        del columns_df
        gc.collect()

        end_time = time.time() - start_time
        
        return render_template('home_page.html', columns=columns, end_time=end_time)
    except Exception as e:
        logging.error(f"Error in chat route: {e}")
        return f"An error occurred: {e}", 500

@app.route('/load_data')
def load_data():
    def generate():
        try:
            # Use chunking to retrieve data
            chunk_size = 50
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
                # Convert chunk to dictionary
                chunk_data = chunk.where(pd.notnull(chunk), None).to_dict(orient='records')
                # Replace NaN with None
                chunk_data = [{k: None if v != v else v for k, v in row.items()} for row in chunk_data]
                # Update total rows processed
                total_rows_processed += len(chunk_data)
                # Yield each chunk as JSON
                yield json.dumps({
                    'rows': chunk_data,
                    'total_processed': total_rows_processed
                }) + '\n'
        except Exception as e:
            logging.error(f"Error in data generation: {e}")
            yield json.dumps({"error": str(e)})
    return Response(generate(), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)