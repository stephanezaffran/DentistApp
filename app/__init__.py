# import sys
# project_home = '/home/stephanezaffran/DentistApp'
# if project_home not in sys.path:
#     sys.path = [project_home] + sys.path


from flask import Flask
from app.models import db, User

from app.services import google_service


from .main import main_blueprint
from .auth import auth_blueprint
from .google import google_blueprint
from app.config import Config
from flask_login import LoginManager


def create_app():

    dentist_app = Flask(__name__)
    dentist_app.config.from_object(Config)

    #migrate.init_app(dentist_app, db)

    db.init_app(dentist_app)
    login_manager = LoginManager()
    login_manager.init_app(dentist_app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    dentist_app.register_blueprint(main_blueprint)
    dentist_app.register_blueprint(auth_blueprint)

    return dentist_app
