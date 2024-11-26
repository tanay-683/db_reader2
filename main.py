from flask import Flask, request, render_template, jsonify, Response
import logging
from src.db_reader.sql_connection.connection import engine
import pandas as pd
import json
import time

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route("/chat", methods=["GET", 'POST'])
def chat():
    try:
        start_time = time.time()
        
        # Fetch columns first
        columns_query = "SELECT top 1000 * FROM Acc_Voucher_Details"
        columns_df = pd.read_sql(columns_query, engine)
        columns = columns_df.columns.tolist()
        
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
            query = "SELECT top 1000 * FROM Acc_Voucher_Details"
            # Track total rows processed
            total_rows_processed = 0
            # Use chunking parameter in read_sql
            for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
                # Convert chunk to list of lists
                chunk_data = chunk.where(pd.notnull(chunk), None).values.tolist()
                # Replace NaN with null
                chunk_data = [[None if x != x else x for x in row] for row in chunk_data]
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