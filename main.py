from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import logging,json, time, datetime
import pandas as pd

from src.db_reader.preprocessing.preprocess import ChunkCleaningPipeline
# from db_reader.nl_to_sql.nl_to_sql import generate_sql_query
from db_reader.config.config import CHUNK_SIZE
from db_reader.config.config import QueryEngine
from db_reader.config.config import engine
from db_reader.config.config import SettingConfigurationManager

app = Flask(__name__)

# setting_config_manager = SettingConfigurationManager()
queryEngine = QueryEngine()


@app.route('/', methods=["GET", 'POST'])
def login():
    if request.method == "POST":
        return redirect(url_for('chat'))    
    return render_template('login.html')


@app.route("/chat", methods=["GET", 'POST'])
def chat(): 
    return render_template('home_page.html')


@app.route('/load_data')
def load_data():
    # query = request.args.get('query', None)
    query = request.args.get('query', None)

    sql_query = queryEngine.generate_sql_query(query)
    logging.info(f"\n\n SQL Query generated: {sql_query}\n\n")
    
    
    if not query:
        def generate():
            yield json.dumps({"error": "No query submitted"}) + '\n'
        return Response(generate(), mimetype='application/json')

    def generate():
        try:
            has_columns_sent = False
            start_time = time.time()
            
            chunk_size = CHUNK_SIZE
            total_rows_processed = 0
            
            for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
                for col in chunk.columns:
                    if chunk[col].dtype == 'datetime64[ns]':
                        chunk[col] = chunk[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                    elif chunk[col].dtype == 'object':
                        chunk[col] = chunk[col].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, datetime.date) else x)
                
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
                
                total_rows_processed += len(chunk)
                
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
                print("="*60)
        
        except Exception as e:
            logging.error(f"Error in data generation: {e}")
            yield json.dumps({"error": str(e)}) + '\n'
    
    return Response(generate(), mimetype='application/json',status=200)

@app.route("/try")
def try_page():
    return render_template('try.html')






if __name__ == '__main__':
    app.run(debug=True)