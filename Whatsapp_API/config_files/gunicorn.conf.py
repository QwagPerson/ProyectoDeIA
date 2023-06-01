import datetime
import os

# Non logging stuff
bind = "localhost:8080"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"

# Logging stuff

# Check if the logs directory exists if not, create it
if not os.path.exists("./logs"):
    os.mkdir("./logs")

if not os.path.exists("./logs/gunicorn"):
    os.mkdir("./logs/gunicorn")

curr_datetime_str = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# Access log - records incoming HTTP requests
accesslog_name = f"{curr_datetime_str}.gunicorn.error.log"
accesslog = f"./logs/gunicorn/{accesslog_name}"

# Error log - records Gunicorn server goings-on
errorlog_name = f"{curr_datetime_str}.gunicorn.access.log"
errorlog = f"./logs/gunicorn/{errorlog_name}"

# Whether to send Fast API output to the error log
capture_output = True

# Check if symlink exists pointing to the latest log file
last_acc_link = "./logs/gunicorn/latest.access.log"
if os.path.exists(last_acc_link):
    os.remove(last_acc_link)
os.symlink(accesslog_name, last_acc_link)

last_err_link = "./logs/gunicorn/latest.error.log"
if os.path.exists(last_err_link):
    os.remove(last_err_link)
os.symlink(errorlog_name, last_err_link)

# How verbose the Gunicorn error logs should be
loglevel = "info"

ROOT_PATH = "/api"
