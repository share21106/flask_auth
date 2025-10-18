from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from .models import User

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_model = User(g.db.users)
        created = user_model.create_user(username, password)
        if created:
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        flash('User already exists', 'warning')
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_model = User(g.db.users)
        if user_model.verify(username, password):
            session['user'] = username
            flash('Logged in successfully', 'success')
            return redirect(url_for('main.home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out', 'info')
    return redirect(url_for('main.home'))
