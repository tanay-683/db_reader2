from pathlib import Path
import os
import logging

project_name = "db_reader"

logging.basicConfig(level=logging.INFO, format="%(asctime)s :: %(message)s")

list_of_files = [
    f"src/{project_name}/__init__.py",
    f"src/{project_name}/model",
    f"src/{project_name}/sql_connection",
    f"templates",
    
    f"src/{project_name}/model/__init__.py",
    f"src/{project_name}/model/model.py",
    
    f"src/{project_name}/sql_connection/__init__.py",
    f"src/{project_name}/sql_connection/connection.py",
    
    f"templates/index.html",
    f"static/css",
    f"research",
    "main.py",
]

for file_path in list_of_files:
    file_path = Path(file_path) # convert to Path object toh handle forward and backward slash problem
    file_dir, file_name = os.path.split(file_path)
    
    if file_dir != "":
        os.makedirs(file_dir, exist_ok=True)
        logging.info(f"Created directory: {file_dir} for the file: {file_name}")
    
    if (not os.path.exists(file_path)) or os.path.getsize(file_path) == 0:
        with open(file_path, "w") as f:
            f.write("")
        logging.info(f"Empty File Created: {file_name}")
    else:
        logging.info(f"File already exists: {file_name}")
