from flask import Blueprint, render_template, g, session
from .models import User

bp = Blueprint('main', __name__, url_prefix='')


@bp.route('/')
def home():
    username = session.get('user')
    return render_template('home.html', username=username)
