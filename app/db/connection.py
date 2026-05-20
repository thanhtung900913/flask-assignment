import os

from dotenv import load_dotenv
from psycopg2 import pool
from flask import current_app
load_dotenv()

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=current_app.config["DB_HOST"],
    port=current_app.config["DB_PORT"],
    database=current_app.config["DB_NAME"],
    user=current_app.config["DB_USER"],
    password=current_app.config["DB_PASSWORD"]
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)