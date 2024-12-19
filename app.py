#app.py

from flask import Flask, render_template, redirect, url_for, request, flash, session
from extensions import db, bcrypt  # Import db and bcrypt from extensions
from models_user import User, GameDayPlayer # Import models after initializing extensions
from models_match import Match  
from datetime import datetime
import os
import logging



app = Flask(__name__)
app.secret_key = os.urandom(24)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/maria/Desktop/New_folder/TTMS/instance/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with app
db.init_app(app)
bcrypt.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        player_email = request.form['player_email']
        password = request.form['password']

        # Query user by username
        user = User.query.filter_by(player_email_address = player_email).first()
        print(f"User: {user}")

        if user:
            print(f"Stored Hashed Password: {user.player_password}")
            print(f"Attempted Plain Password: {password}")

        if user and bcrypt.check_password_hash(user.player_password, password):
            session['user_id'] = user.player_id
            session['user_role'] = user.player_role
            session['user_name'] = user.player_login_name
            flash('Login successful!', 'success')

            # Redirect based on role
            if user.player_role == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('users'))

        flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #checks if user already exists in database:
    if request.method == 'POST':
        user_name = request.form['nickname']
        user_email = request.form['email']
        user_phone_number = request.form['phone']
        password = request.form['password']

        # Query user by email
        user = User.query.filter_by(player_email_address=user_email).first()
        # Query user to determine preliminary rank of any new player defined as number of players/3
        new_user_rank = round(User.query.count()/3,3)

        if user:
            flash('User details already in database. Please login instead.', 'danger')
            return redirect(url_for('login'))
        
        new_user = User(
            player_login_name=user_name,
            player_email_address=user_email,
            player_phone_number=user_phone_number,
            player_password=bcrypt.generate_password_hash(password).decode('utf-8'),
            player_role='user',
            player_rank=new_user_rank
        )

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('signup_success'))
        
        
    return render_template('signup.html')


@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')


@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    from gameday import GameDay, serialize_gameday_obj
    admin_name = session.get('user_name')
    gameday_obj = GameDay()
    print(f'Accessing four matches list from /admin')
    gameday_obj.display_four_matches_list_details
    return render_template('admin.html',user_name = admin_name, four_matches_list = gameday_obj.create_four_matches())



@app.route('/admin/submit_match_results', methods=['GET', 'POST'])
def submit_match_results():
    player1 = request.form.get('player1_login_name')
    player2 = request.form.get('player2_login_name')
    last_played = match_start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    admin_name = session.get('user_name')
    
    game_results = []
    for i in range(1, 6):
        game1_score = request.form.get(f'player1_game_{i}')
        game2_score = request.form.get(f'player2_game_{i}')
        if game1_score and game2_score:
            game_results.append((game1_score, game2_score))
    
    match_result = str(tuple(game_results))

    played_match = Match(
        match_start_date_time = match_start_date,
        player_1_login_name=player1,
        player_2_login_name=player2,
        match_result=match_result
    )
    db.session.add(played_match)
    db.session.commit()
    
    gameday_obj = GameDay()
    print('Accessing four matches list prior to match status update from /admin/submit_match_results')
    gameday_obj.display_four_matches_list_details()
    gameday_obj.update_match_status(played_match=played_match, match_status = 'played')
    print('Match status updated')
    print('Accessing four matches list after match status update from /admin/submit_match_results')
    gameday_obj.display_four_matches_list_details()
    gameday_obj.update_gameday_player(player_1_login_name = player1, player_2_login_name = player2, status='reserve', last_played=last_played)
        
    return render_template('admin.html', user_name = admin_name, four_matches_list = gameday_obj.create_four_matches())


@app.route('/admin/refresh', methods=['GET', 'POST'])
def refresh():
    admin_name = session.get('user_name')
    gameday_obj = GameDay()
    return render_template('admin.html',user_name = admin_name, four_matches_list = gameday_obj.create_four_matches())


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/users/payment')
def user_payment():
    #redirects to Stripe or pay in cash at the venue. Payment status in ['paid','unpaid','deferred']
    pass

@app.route('/cash_payment')
def cash_payment():
    #change booking payment status to Paid in Full
    pass

from models_booking import Booking

@app.route('/users', methods=['GET', 'POST'])
#to add:
# Summary of user details including current ranking
#upon clicking on Make a booking button redirects to payment page

def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_name = session.get('user_name')
    
    from models_booking import find_available_bookings, retrieve_all_bookings_for_user
    all_available_bookings_period_60_days = find_available_bookings()
    formatted_all_available_bookings_period_60_days = [
        {
            'original': date,
            'formatted': datetime.strptime(date, '%Y-%m-%d').strftime('%d-%b-%Y, %A')
        } 
        for date in all_available_bookings_period_60_days
    ]
    available_user_booking = retrieve_all_bookings_for_user(user_name=user_name)
    formatted_available_user_booking = [
        {
            'original': date,
            'formatted': datetime.strptime(date, '%Y-%m-%d').strftime('%d-%b-%Y, %A')
        } 
        for date in available_user_booking
    ]
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'new_booking':
            selected_available_date = request.form.get('choose_available_booking_date')
                        
            if selected_available_date:
                new_booking = Booking(date_time_booking_made = datetime.now(),player_login_name = user_name, 
                                required_booking_date = selected_available_date)
                db.session.add(new_booking)
                db.session.commit()
                flash(f'You are booked for {selected_available_date}. See you there!','success')
                available_user_booking = retrieve_all_bookings_for_user(user_name=user_name) #refresh available dates for drop-down list
            else:
                flash('No booking made!','danger')
        elif action == 'delete_booking':
                selected_date_to_delete = request.form.get('delete_booking_date')
                if selected_date_to_delete:
                    booking_to_delete = Booking.query.filter_by(required_booking_date=selected_date_to_delete, player_login_name=user_name).first()
                    db.session.delete(booking_to_delete)
                    db.session.commit()
                    flash(f"Booking on {selected_date_to_delete} deleted successfully.",'success')
                    available_user_booking = retrieve_all_bookings_for_user(user_name=user_name) #refresh available dates for drop-down list
                else:
                    flash(f"No booking found for {selected_date_to_delete}.",'danger')
    
    return render_template('user.html', 
                       all_available_bookings_period_60_days=formatted_all_available_bookings_period_60_days,
                       available_user_booking = formatted_available_user_booking, user_name = user_name)



if __name__ == '__main__':
    app.run(debug=True)
