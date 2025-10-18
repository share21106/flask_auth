from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='')

# The blueprint expects a `User` model wrapper in models.py that accepts
# a collection-like object (e.g. g.db.users) and provides at least:
# - create_user(username, password) -> bool (True if created, False if user exists)
# - verify(username, password) -> bool (True if credentials valid)
#
# If you already have a models.User, the code below will use it. If not,
# the fallback class below implements the minimal behavior using the
# provided collection's find_one / insert_one / update_one methods.
try:
    from .models import User as UserModel  # your existing model (recommended)
except Exception:
    UserModel = None


class _FallbackUser:
    """Minimal drop-in user helper that stores password_hash in the collection."""
    def __init__(self, collection):
        self.collection = collection

    def create_user(self, username: str, password: str) -> bool:
        if not username:
            return False
        if self.collection.find_one({"username": username}):
            return False
        password_hash = generate_password_hash(password)
        try:
            self.collection.insert_one({"username": username, "password_hash": password_hash})
            return True
        except Exception:
            return False

    def verify(self, username: str, password: str) -> bool:
        user = self.collection.find_one({"username": username})
        if not user:
            return False
        stored = user.get("password_hash") or user.get("password")
        if not stored:
            return False
        # If stored is plain (unlikely), allow check_password_hash to handle
        try:
            return check_password_hash(stored, password)
        except Exception:
            return False


def _get_user_model():
    """Return an instance of the application's User wrapper using g.db.users."""
    collection = getattr(g, "db", None)
    if not collection:
        raise RuntimeError("Database not attached to g (ensure app.before_request attaches g.db).")
    users_col = getattr(collection, "users", None) or collection  # allow either g.db.users or g.db itself
    if UserModel:
        return UserModel(users_col)
    return _FallbackUser(users_col)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = (request.form.get('username') or "").strip()
        password = request.form.get('password') or ""
        confirm = request.form.get('confirm_password') or request.form.get('confirm') or ""

        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm:
            flash('Passwords do not match.', 'warning')
            return redirect(url_for('auth.register'))

        user_model = _get_user_model()
        # Use create_user() if available, otherwise fallback will handle insertion
        created = False
        try:
            created = user_model.create_user(username, password)
        except Exception as e:
            # In case the real model raises a duplicate-key or other error, handle gracefully
            # You can log e for debugging if you have a logger attached to the app.
            created = False

        if created:
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('User already exists or registration failed.', 'warning')
            return redirect(url_for('auth.register'))

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or "").strip()
        password = request.form.get('password') or ""

        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return redirect(url_for('auth.login'))

        user_model = _get_user_model()
        try:
            valid = user_model.verify(username, password)
        except Exception:
            valid = False

        if valid:
            session['user'] = username
            flash('Logged in successfully', 'success')
            return redirect(url_for('main.home'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out', 'info')
    return redirect(url_for('main.home'))