from flask import render_template, request, session

from ttms import app
from ttms.general_use_functions import build_web_page,redirect_to_web_page,display_message_on_page
from ttms.login import login_and_store_data
from ttms.sign_up import signup_user
from ttms.admin import login_check_and_redirect
from ttms.submit_match_results import obtain_match_results_and_update_session
from ttms.create_match_by_system import system_chooses_next_match
from ttms.users import make_or_delete_booking, obtain_info_and_load_page
from ttms.create_match_manually import choose_players_and_create_match_manually
from ttms.payment_success import check_payment_status_update_database


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


@app.route('/admin/<check_availability_matches>')
def admin(check_availability_matches):    
    return login_check_and_redirect(check_availability_matches)


@app.route('/admin/submit_match_results', methods=['GET', 'POST'])
def submit_match_results():
    return obtain_match_results_and_update_session()


@app.route('/admin/create_match_manually',methods = ['GET','POST'])
def create_match_manually():
    return choose_players_and_create_match_manually()


@app.route('/admin/create_match_by_system', methods = ['GET','POST'])
def create_match_by_system():
    return system_chooses_next_match()

@app.route('/logout')
def logout():
    session.clear()
    return redirect_to_web_page('login')

@app.get('/users')
def users_get():
    return obtain_info_and_load_page()


@app.post('/users')
def users_post():
     return make_or_delete_booking()


@app.route('/user/payment_success')
def success():
    return check_payment_status_update_database()

@app.route('/user/payment_cancel')
def cancel():
    display_message_on_page("Payment canceled by Stripe. Please try again.",'danger')
    return redirect_to_web_page('users_get')

