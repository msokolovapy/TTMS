#app.py

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import User
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a secure random key for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['user_email']
        password = request.form['password']

        # Query user by username
        user = User.query.filter_by(user_email = user_email).first()

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


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #checks if user already exists in database:
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_phone_number = request.form['user_phone_number']
        user_email = request.form['user_email']
        password = request.form['password']

        # Query user by email
        user = User.query.filter_by(user_email=user_email).first()

        if user:
            flash('User details already in database. Please login instead.', 'danger')
            return redirect(url_for('login'))
        
        new_user = User(
            user_name=user_name,
            User_email=user_email,
            user_phone_number=user_phone_number,
            password=bcrypt.generate_password_hash(password).decode('utf-8')
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signup_successful'))
        
    return render_template('signup.html')


@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')


@app.route('/users')
#Summary of user details including current ranking
#displays 'Let's make a booking:' string	
#at initiation checks ttms.db to see which booking dates are available
#displays available booking dates as date picker and button 'Make a booking'
#upon clicking on Make a booking button redirects to payment page
def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('user.html')

@app.route('/admin')
#displays 4 sectors with the following styling/information:
	#'Match between' {player_1_login_name} and {player_2_login_name} and Edit button
		#Edit button will allow for admin to change players and accept cash payments 
	#Scores as form with {player_1_login_name} and {player_2_login_name} as a header and game 1,...,game N as rows
	#Update Match Result button
def admin():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/users/payment')
def user_payment():
    #redirects to Paypal or pay in cash at the venue

@app.route('/cash_payment')
def cash_payment():
    #change booking payment status to Paid in Full


if __name__ == '__main__':
    app.run(debug=True)
