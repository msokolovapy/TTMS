from flask import Flask, render_template, redirect, url_for, request, flash, session
import sys,os
sys.path.append(os.path.abspath('C:/Users/maria/Desktop/New_folder/TTMS/TTMS/'))
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import User,db,bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a secure random key for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query user by username
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            flash('Login successful!', 'success')

            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('users'))

        flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

@app.route('/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('user.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
