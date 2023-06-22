from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__, template_folder='templates', static_folder='./static')

from app.auth import views

