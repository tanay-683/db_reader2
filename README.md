# db_reader2
# To-do

## RAG
- text file with table names and explanation
- add table info with 3 rows as example

## Features
- configuration page
    - involves model selection, embedding selection, dark and light mode,
- `export table` button
- ask model name
- table UI

## Development
- remove langchain
- add logging and error handling
- add tests
- how to load all model/embeddings only once and store them in memory

    Concept: Environment Persistence in Flask

    When using Flask, the application runs as a long-lived server process. This means resources initialized when the server starts can persist throughout the server's lifecycle. This persistence is ideal for heavy objects like machine learning models or database connections because they are loaded once and reused for each incoming request.
    How It Works in Flask

        Application Factory Pattern: Initialize resources when creating the Flask app. This allows modular and clean management of resources.
        Application Context: Store resources in the Flask app's config or a custom attribute for global access.
        Lazy Initialization: Load resources only when first accessed (optional, for performance).
        Request-Scoped or App-Scoped Resources:
            Request-scoped: Resources that are initialized and disposed of for each request.
            App-scoped: Resources that persist for the entire app lifecycle.

    Implementation: Loading Models and Query Engine in Flask

    Here’s how you can set it up:
    Step 1: Structure Your Flask App

    Use the application factory pattern to create your Flask app. Initialize heavy resources once and reuse them.
    ``` python

    from flask import Flask, request, jsonify
    from llama_index.core import Settings
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core.query_engine import NLSQLTableQueryEngine
    from db_reader.model.model import get_gemini_model
    from db_reader.sql_connection.connection import sql_database
    import logging

    # Resource Manager
    class ResourceManager:
        def __init__(self):
            self.embedding_model = None
            self.query_engine = None

        def get_embedding_model(self):
            if self.embedding_model is None:
                logging.info("Loading HuggingFace embedding model!!")
                self.embedding_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2")
                logging.info("HuggingFace embedding model loaded!!")
            return self.embedding_model

        def get_query_engine(self):
            if self.query_engine is None:
                if Settings.embed_model is None:
                    Settings.embed_model = self.get_embedding_model()
                if Settings.llm is None:
                    Settings.llm = get_gemini_model()
                self.query_engine = NLSQLTableQueryEngine(
                    sql_database=sql_database,
                    tables=["Customer", "LMS_Loan_Master"],
                    llm=Settings.llm
                )
            return self.query_engine

    # Application Factory
    def create_app():
        app = Flask(__name__)

        # Initialize ResourceManager and attach it to the app
        resource_manager = ResourceManager()
        app.config['RESOURCE_MANAGER'] = resource_manager

        # Define a test route
        @app.route('/query', methods=['POST'])
        def handle_query():
            query = request.json.get('query')
            query_engine = app.config['RESOURCE_MANAGER'].get_query_engine()
            result = query_engine.query(query)
            return jsonify(result)

        return app
    ```
    Step 2: Run the Flask App

    Run the app using the Flask CLI or any WSGI server.
    ``` bash
    export FLASK_APP=myapp
    flask run
    ```

    Replace myapp with the name of your script (e.g., app.py).
    Advantages of This Approach

        Centralized Management: Resources like models and query engines are managed in a single place (the ResourceManager).
        Performance: Heavy resources are loaded only once at startup, reducing request processing time.
        Modularity: Using the application factory pattern enables better testing and modularity.
        Scalability: Combine with Flask extensions like Gunicorn or uWSGI for robust scaling.
        Flexibility: Add more shared resources (e.g., database connections, caching systems) using the same pattern.

    Other Use Cases for Persistent Resources in Flask

        Machine Learning Models: Load and reuse ML models for inference.
        Database Connections: Maintain persistent database connections to avoid reconnecting on every request.
        API Clients: Reuse clients for external APIs (e.g., AWS SDK, HTTP clients).
        Caching: Use libraries like Flask-Caching for shared caching layers.
        Task Queues: Attach queue workers (e.g., Celery) for background tasks.

    Extending the Concept

    You can expand the approach by integrating tools and patterns:

        Flask Extensions: Use Flask extensions for database handling (Flask-SQLAlchemy), caching, etc.
        Blueprints: Modularize your app further with Blueprints.
        Dependency Injection: Use libraries like Flask-Injection to inject dependencies dynamically.
        Distributed Systems: Use a service like Redis or RabbitMQ for managing shared states or tasks.

    This architecture ensures high performance, maintainability, and scalability for your Flask application.