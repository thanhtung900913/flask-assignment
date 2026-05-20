import os
import dotenv

dotenv.load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES'))
    DB_HOST = os.getenv('HOST')
    DB_PORT = int(os.getenv('PORT'))
    DB_NAME = os.getenv('DATABASE')
    DB_USER = os.getenv('USER')
    DB_PASSWORD = os.getenv('PASSWORD')
    JWT_BLOCKLIST_ENABLED = True
    JWT_TOKEN_LOCATION = ["headers"]