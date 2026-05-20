from flask import Flask

from app.utils.extensions import jwt
from app.routes.auth_route import auth_bp
from app.routes.device_route import device_bp
from app.routes.favourite_class_route import favourite_class_bp
from app.config import Config

app = Flask(__name__)

app.config.from_object(Config)

jwt.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(device_bp, url_prefix='/devices')
app.register_blueprint(favourite_class_bp, url_prefix='/favourites')

if __name__ == '__main__':
    app.run(debug=True)