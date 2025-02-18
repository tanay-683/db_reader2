import logging, os, sys

logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(filename)s: %(lineno)d: %(message)s:]"

log_dir = "logs"

log_filepath = os.path.join(log_dir, "running_logs.log")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level =logging.INFO,
    format = logging_str,

    handlers=[
        logging.FileHandler(log_filepath), # this will create log files in workspace 
        logging.StreamHandler(sys.stdout) # this will print the log at terminal
    ]
)


