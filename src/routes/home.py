from flask import Blueprint, render_template, redirect, url_for, session

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('users.login'))
    return render_template('dashboard.html')  # Or a homepage template