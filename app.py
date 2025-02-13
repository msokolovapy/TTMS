#app.py
from flask import Flask, render_template, redirect, url_for, request, flash, session
from extensions import db, bcrypt
from models_user import User
from models_match import Match  
from datetime import datetime
import os
import stripe



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
        user = User.query.filter_by(player_email_address = player_email).first()

        if user and bcrypt.check_password_hash(user.player_password, password):
            session['user_id'] = user.player_id
            session['user_role'] = user.player_role
            session['user_name'] = user.player_login_name
            session['player_rank'] = user.player_rank
            flash('Login successful!', 'success')

            if user.player_role == 'admin':
                from gameday import GameDay, serialize_gameday_obj
                gameday_obj = GameDay()
                serialize_gameday_obj(session, gameday_obj)

                from gameday import display_gameday_matches
                print('Gameday matches at admin login:')
                print(100*'=')
                display_gameday_matches(gameday_obj.get_gameday_matches())

                return redirect(url_for('admin'))
            else:
                return redirect(url_for('users'))

        flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['nickname']
        user_email = request.form['email']
        user_phone_number = request.form['phone']
        password = request.form['password']

        user = User.query.filter_by(player_email_address=user_email).first()
        new_user_rank = 1500

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
    admin_name = session.get('user_name')
    from gameday import deserialize_gameday_obj
    restored_gameday_obj = deserialize_gameday_obj(session=session)
    return render_template('admin.html',user_name = admin_name, four_matches_list = restored_gameday_obj.create_four_matches())


@app.route('/admin/submit_match_results', methods=['GET', 'POST'])
def submit_match_results():
    from models_match import get_match_results
    player1 = request.form.get('player1_login_name')
    player2 = request.form.get('player2_login_name')
    last_played = match_start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    match_result = get_match_results()

    played_match = Match(
        match_start_date_time = match_start_date,
        player_1_login_name=player1,
        player_2_login_name=player2,
        match_result=match_result
    )
    db.session.add(played_match)
    db.session.commit()

    
    from gameday import deserialize_gameday_obj, serialize_gameday_obj
    gameday_obj = deserialize_gameday_obj(session= session)
    gameday_obj.update_match(match_to_update=played_match, match_status = 'played')
    gameday_obj.update_gameday_player(player_1_login_name = player1, player_2_login_name = player2, status='reserve', last_played=last_played)
    serialize_gameday_obj(session = session, gameday_obj=gameday_obj)

    return redirect(url_for('admin'))

@app.route('/admin/create_match_manually',methods = ['GET','POST'])
def create_match_manually():
    from gameday import deserialize_gameday_obj,serialize_gameday_obj,create_drop_down_list
    restored_gameday_obj = deserialize_gameday_obj(session=session)
    clicked_button = request.form.get('edit_button')
    
    if clicked_button == 'manually_edit_players':
        sorted_serialized_players_list = restored_gameday_obj.sort_gameday_players()
        drop_down_list = create_drop_down_list(sorted_serialized_players_list)

        return render_template('admin_create_match_manually.html', \
                            drop_down_list = drop_down_list)

    elif clicked_button == 'submit_updated_players':
        player_1_original_login_name = request.form.get('player_1_original_login_name')
        player_2_original_login_name = request.form.get('player_2_original_login_name')
        player_1_updated_login_name = request.form.get('player_1_updated_login_name')
        player_2_updated_login_name = request.form.get('player_2_updated_login_name')

        match_to_update = Match(player_1_original_login_name,player_2_original_login_name)
        restored_gameday_obj.update_match(match_to_update,player_1_updated_login_name, player_2_updated_login_name, 'active')
        serialize_gameday_obj(session = session, gameday_obj=restored_gameday_obj)

        return redirect(url_for('admin'))
                    

@app.route('/admin/create_match_by_system', methods = ['GET','POST'])
def create_match_by_system():
    """This function receives player login names from an html form, creates match object, 
    updates match object status to 'played' and randomly selects any 'active' match from 
    gameday object's gameday_matches list to be displayed on html form 
    """
    player_1_login_name = request.form.get('player_1_login_name')
    player_2_login_name = request.form.get('player_2_login_name')
    admin_name = session.get('user_name')
    match_to_update = Match(player_1_login_name, player_2_login_name)
    

    from gameday import deserialize_gameday_obj,serialize_gameday_obj
    restored_gameday_obj = deserialize_gameday_obj(session=session)
    counter_active_matches = restored_gameday_obj.counter_active_matches()
    if counter_active_matches == 0:
        flash('No more matches planned for today. \
                    Please create a match manually via Edit button', 'info') 
        serialize_gameday_obj(session, restored_gameday_obj)
        return render_template('admin.html',user_name = admin_name,
                                    four_matches_list = restored_gameday_obj.create_four_matches(),
                                     check_availability_matches = False)
    
    else:
        restored_gameday_obj. update_match(match_to_update,match_status = 'played',match_html_display_status = False)
        any_active_match = restored_gameday_obj.find_specified_match(match_status = 'active', match_html_display_status = False)
        restored_gameday_obj.update_match(match_to_update=any_active_match, \
                                        match_html_display_status=True)
        serialize_gameday_obj(session,restored_gameday_obj)
        return redirect(url_for('admin'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/users', methods=['GET', 'POST'])
#to add:
# Summary of user details including current ranking
def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from models_booking import Booking, Payment,find_available_bookings, retrieve_all_bookings_for_user,format_dates_for_display
    from stripe_checkout import create_stripe_session
    user_name = session.get('user_name')
    player_rank = session.get('player_rank')
    formatted_all_available_bookings_period_60_days = format_dates_for_display(find_available_bookings(user_name))
    formatted_available_user_booking = format_dates_for_display(retrieve_all_bookings_for_user(user_name))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'new_booking':
            selected_available_date = request.form.get('choose_available_booking_date')
            if selected_available_date:
                new_booking = Booking(date_time_booking_made = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),player_login_name = user_name, \
                                      required_booking_date = selected_available_date)
                db.session.add(new_booking)
                db.session.commit()
                new_payment = Payment(fk_booking_id = new_booking.booking_id, payment_status = 'unpaid')
                db.session.add(new_payment)
                db.session.commit()
                stripe_session = create_stripe_session(new_booking.booking_id)
                new_payment.stripe_session_id = stripe_session.id
                db.session.commit()
                flash(f"You are booked for {datetime.strptime(selected_available_date, '%Y-%m-%d').strftime('%d-%b-%Y')}.\
                     See you there!",'success')
                return redirect(stripe_session.url, code=303)
            else:
                flash('No booking made!','danger')

        elif action == 'delete_booking':
            from models_booking import refund_eligibility_check
            selected_date_to_delete = request.form.get('delete_booking_date')
            booking_to_delete = Booking.query.filter_by(required_booking_date=selected_date_to_delete, player_login_name=user_name).first()
            payment_to_delete = Payment.query.filter_by(fk_booking_id = booking_to_delete.booking_id).first()
            if refund_eligibility_check(selected_date_to_delete):
                from stripe_checkout import restore_stripe_session, obtain_stripe_refund
                stripe_session_id = payment_to_delete.stripe_session_id
                stripe_session = restore_stripe_session(stripe_session_id)
                payment_intent_id = stripe_session.payment_intent
                obtain_stripe_refund(payment_intent_id)
                flash("Your refund is being processed. \
                        The funds should appear in your account within 5-6 business days. \
                        Thank you for your patience.", 'success')
            else:   
                flash("Refund not available: Cancellations must be made at least 24 hours prior to the booking date. \
                        Unfortunately, your cancellation was made too late.", 'danger')   
            
            db.session.delete(payment_to_delete)
            db.session.delete(booking_to_delete)
            db.session.commit()
            flash(f"Booking on {selected_date_to_delete} deleted successfully.",'success')
            return redirect(url_for('users'))

    return render_template('user.html', 
                       all_available_bookings_period_60_days=formatted_all_available_bookings_period_60_days,
                       available_user_booking = formatted_available_user_booking, user_name = user_name, player_rank = player_rank)


@app.route('/user/payment_success')
def success():
    from models_booking import Payment
    booking_id = request.args.get('booking_id')
    stripe.api_key = 'sk_test_51Qmkf8BaZDAfc4fNRXKFyD47bswWxKHpAHD1QDyy7cv3asinDAYCkFt1Tr3kLIx3A9mhjIgz8hPezzHlXTK7sh5V004fxas5eQ'

    try:
        payment = Payment.query.filter_by(fk_booking_id=booking_id).first()
        session = stripe.checkout.Session.retrieve(payment.stripe_session_id)

        if session.payment_status == 'paid':
            payment.payment_status = 'paid'
            payment.date_time_payment_made = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.commit()
            flash("Payment successful! Your booking is confirmed.", 'success')
        else:
            flash("Payment failed or canceled.", 'danger')
    except stripe.error.StripeError as e:
        flash(f"Stripe error: {e.user_message}", 'danger')
    
    return redirect(url_for('users'))


@app.route('/user/payment_cancel')
def cancel():
    flash("Payment canceled by Stripe. Please try again.",'danger')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)