# library zone

# some essential modoule of flask
from flask import Flask, render_template, request, redirect, session, url_for, app
from flask_ngrok import run_with_ngrok

# sql, regex, hash, request, and operating system library
import sqlite3, re, hashlib, requests, os
# use for get vatiable from .env - file environment
from decouple import config
# use for save log in web server
from logging.config import dictConfig
# use for upload file 
from werkzeug.utils import secure_filename

# use for schedule and time activities 
from datetime import timedelta, date, datetime
from pytz import utc
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler

# define project path of database
PATH = '/app/base/test.db'

# defince upload image path for project
IMG_PATH = '/app/base/static/img'

# set file extension for uploading    
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# setup basic part of web
# get name of app and start app with ngrok
app = Flask(__name__) 

# using for ngrok detect app
run_with_ngrok(app)

# config log format file for flask
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | %(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'test.log',
                'maxBytes': 4194304, 
                'backupCount': 10,
                'level': 'DEBUG',
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},
    }
)

# using for connecting to database and get data, return list, can commit change
def get_db_connection(path):
    conn = sqlite3.connect(path) 
    conn.row_factory = sqlite3.Row
    return conn 

# same above, return tuple, can't commit change
def get_data(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    return cursor 

# md5 hash input, using for making password more security
def encrypt(data):
    return str(hashlib.md5(data.encode()).hexdigest())

def validate_input(input):
    regex = r"(\s*([\0\b\'\"\n\r\t\%\_\\]*\s*(((select\s*.+\s*from\s*.+)|(select\s*.+\s*if\s*.+)|(union\s*.+\s*select\s*.+)|(insert\s*.+\s*into\s*.+)|(update\s*.+\s*set\s*.+)|(delete\s*.+\s*from\s*.+)|(drop\s*.+)|(truncate\s*.+)|(\s*.+#|--)|(alter\s*.+)|(exec\s*.+)|(\s*(all|any|not|and|between|in|like|or|some|contains|containsall|containskey|where|sleep|waitfor|delay)\s*.+[\=\>\<=\!\~]+.+)|(let\s+.+[\=]\s*.*)|(begin\s*.*\s*end)|(\s*[\/\*]+\s*.*\s*[\*\/]+)|(\s*(\-\-)\s*.*\s+)|(\s*(contains|containsall|containskey)\s+.*)))(\s*[\;]\s*)*)+)"
    if re.match(regex, input):
        return False
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# setup shedule mode
executors = {
    'default': ThreadPoolExecutor(20), # max thread
    'processpool': ProcessPoolExecutor(5) # min thread
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

sched = BackgroundScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
