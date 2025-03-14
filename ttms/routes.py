from datetime import datetime
import stripe
from flask import render_template, redirect, url_for, request, flash, session

from ttms import app,db
from ttms.login import login_and_store_data,build_web_page,redirect_to_web_page
from ttms.sign_up import signup_user
from ttms.admin import login_checks_pass, obtain_info_from_
from ttms.submit_match_results import obtain_match_results_and_update_session
from ttms.models_match import Match
from ttms.models_booking import Booking, Payment,find_available_bookings, refund_eligibility_check,retrieve_all_bookings_for_user,format_dates_for_display
from ttms.gameday import serialize_,deserialize_, create_drop_down_list
from ttms.models_booking import Payment
from ttms.stripe_checkout import create_stripe_session, restore_stripe_session, obtain_stripe_refund


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        return login_and_store_data()
    return build_web_page('login')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return signup_user()
    return build_web_page('signup')


@app.route('/admin')
def admin():
    if login_checks_pass():
          admin_name,matches = obtain_info_from_(session)
          return build_web_page('admin', admin_name, matches.to_display())
    return redirect_to_web_page('login')

@app.route('/admin/submit_match_results', methods=['GET', 'POST'])
def submit_match_results():
    return obtain_match_results_and_update_session()


@app.route('/admin/create_match_manually',methods = ['GET','POST'])
def create_match_manually():
    matches = deserialize_('matches')
    clicked_button = request.form.get('edit_button')
    
    if clicked_button == 'manually_edit_players':
        sorted_serialized_players_list = matches.sort_gameday_players()
        drop_down_list = create_drop_down_list(sorted_serialized_players_list)

        return render_template('admin_create_match_manually.html', \
                            drop_down_list = drop_down_list)

    elif clicked_button == 'submit_updated_players':
        player_1_original_login_name = request.form.get('player_1_original_login_name')
        player_2_original_login_name = request.form.get('player_2_original_login_name')
        player_1_updated_login_name = request.form.get('player_1_updated_login_name')
        player_2_updated_login_name = request.form.get('player_2_updated_login_name')

        match_to_update = Match(player_1_original_login_name,player_2_original_login_name)
        matches.update_match(match_to_update,player_1_updated_login_name, player_2_updated_login_name, 'active')
        serialize_(matches)

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
    
    matches = deserialize_('matches')
    counter_active_matches = matches.counter_active_matches()
    if counter_active_matches == 0:
        flash('No more matches planned for today. \
                    Please create a match manually via Edit button', 'info') 
        serialize_(matches)
        return render_template('admin.html',user_name = admin_name,
                                    four_matches_list = matches.to_display(),
                                     check_availability_matches = False)
    
    else:
        matches. update_match(match_to_update,match_status = 'played',match_html_display_status = False)
        any_active_match = matches.find_specified_match(match_status = 'active', match_html_display_status = False)
        matches.update_match(match_to_update=any_active_match, \
                                        match_html_display_status=True)
        serialize_(matches)
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
            selected_date_to_delete = request.form.get('delete_booking_date')
            booking_to_delete = Booking.query.filter_by(required_booking_date=selected_date_to_delete, player_login_name=user_name).first()
            payment_to_delete = Payment.query.filter_by(fk_booking_id = booking_to_delete.booking_id).first()
            if refund_eligibility_check(selected_date_to_delete):
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
            flash(f"Booking on {selected_date_to_delete} cancelled successfully.",'success')
            return redirect(url_for('users'))

    return render_template('user.html', 
                       all_available_bookings_period_60_days=formatted_all_available_bookings_period_60_days,
                       available_user_booking = formatted_available_user_booking, user_name = user_name, player_rank = player_rank)


@app.route('/user/payment_success')
def success():
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