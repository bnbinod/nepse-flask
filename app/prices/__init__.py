from flask import Blueprint

bp = Blueprint('prices', __name__)

from app.prices import routes
