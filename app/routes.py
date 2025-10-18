from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from . import mongo

main = Blueprint('main', __name__)

@main.before_app_request
def before_request():
    # store the db in flask.g for access throughout the request
    g.db = mongo.db

@main.route('/')
def index():
    users = list(g.db.users.find())
    return render_template('index.html', users=users)

@main.route('/add', methods=['POST'])
def add_user():
    name = request.form.get('name')
    if not name:
        flash('Name required', 'error')
        return redirect(url_for('main.index'))

    g.db.users.insert_one({'name': name})
    flash('User added successfully!', 'success')
    return redirect(url_for('main.index'))
