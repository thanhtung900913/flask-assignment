from datetime import timedelta
import os

from flask import Flask,jsonify
from dotenv import load_dotenv


from db import get_connection, release_connection
from extensions import jwt
from routes.auth_route import auth_bp
from routes.device_route import device_bp
from routes.favourite_class_route import favourite_class_bp

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES")))
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_BLOCKLIST_ENABLED"] = True

jwt.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(device_bp, url_prefix='/devices')
app.register_blueprint(favourite_class_bp, url_prefix='/favourites')

if __name__ == '__main__':
    app.run(debug=True)