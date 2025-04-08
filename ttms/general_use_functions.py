#general_use_functions.py
from datetime import datetime
from flask import render_template, redirect, url_for, session, flash, request

from ttms import db
from ttms.models_match import Matches, deserialize_, get_match_results
from ttms.models_user import Players, User



def update_database_for(object):
    add_to_database_session(object)
    commit_changes_to_database()

def add_to_database_session(object):
    return db.session.add(object)

def commit_changes_to_database():
    return db.session.commit()

def delete_from_database(object):
    return db.session.delete(object)

def convert_to_boolean(string):
   if string == 'True':
      return True
   return False


def build_web_page(html_file_name,user_name = None,
                   four_matches_list = None,
                   check_availability_matches = None,
                   drop_down_list = None,
                   all_available_bookings_period_60_days = None,
                   available_user_booking = None,
                   player_rank = None ):
    html_file_name += '.html'
    try:
        return render_template(html_file_name,
                                user_name=user_name, 
                                four_matches_list=four_matches_list, 
                                check_availability_matches = check_availability_matches,
                                drop_down_list = drop_down_list,
                                all_available_bookings_period_60_days = all_available_bookings_period_60_days,
                                available_user_booking = available_user_booking,
                                player_rank = player_rank)
    except Exception as e:
        return render_template('error.html') 


def redirect_to_web_page(function_name,check_availability_matches = True):
    try:
        return redirect(url_for(function_name, check_availability_matches = check_availability_matches))
    except Exception:
        return render_template('error.html')


def display_message_on_page(message_str, message_type):
    flash(message_str,message_type)


def update_session_for(data):
    if isinstance(data, User):
        session['user_id'] = data.player_id
        session['user_role'] = data.player_role
        session['user_name'] = data.player_login_name
        session['player_rank'] = data.player_rank
    elif isinstance(data, Matches):
        session['matches'] = data.to_dict()
    elif isinstance(data, Players):
        session['players'] = data.to_dict()


def obtain_info_from_webpage():
    function_name = request.endpoint
    if function_name == 'create_match_manually':   
        clicked_button = request.form.get('edit_button')
        if clicked_button == 'manually_edit_players':
            return None
        elif clicked_button == 'submit_updated_players':
            player_1_original_login_name = request.form.get('player_1_original_login_name')
            player_2_original_login_name = request.form.get('player_2_original_login_name')
            selected_login_name_1 = request.form.get('player_1_updated_login_name')
            selected_login_name_2 = request.form.get('player_2_updated_login_name')
            return player_1_original_login_name, player_2_original_login_name,selected_login_name_1, selected_login_name_2 
    elif function_name == 'login':
        player_email = request.form['player_email']
        password = request.form['password']
        return player_email, password
    elif function_name == 'signup':
        signup_data = {'user_name':request.form['nickname'],
                       'user_email':request.form['email'],
                        'user_phone_number':request.form['phone'],
                        'user_password':request.form['password']}
        return signup_data
    elif function_name == 'submit_match_results':
         match_data = {
                  'match_start_date_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  'player_1_login_name' : request.form.get('player1_login_name'),
                  'player_2_login_name' : request.form.get('player2_login_name'),
                  'match_result' : get_match_results(),
                  }
         player_data = match_data['player_1_login_name'], match_data['player_2_login_name']
         time_last_played = match_data['match_start_date_time']
         return match_data, player_data, time_last_played
    elif function_name == 'create_match_by_system':
        player_1_login_name = request.form.get('player_1_login_name')
        player_2_login_name = request.form.get('player_2_login_name') 
        return player_1_login_name, player_2_login_name      
    elif function_name =='users_post':
        user_intent = request.form.get('action')
        selected_date = request.form.get('date')
        return selected_date, user_intent
    elif function_name == 'success':
        booking_id = request.args.get('booking_id')
        return booking_id
    

def obtain_info_from_session():
    function_name = request.endpoint
    if function_name in ('admin','create_match_by_system'):
        name = session.get('user_name')
        matches = deserialize_('matches')
        return name, matches 
    elif function_name in ('submit_match_results','create_match_manually'):
        matches = deserialize_('matches')
        players = deserialize_('players')
        return matches, players
    elif function_name == 'users_get' or function_name == 'users_post':
        user_name = session.get('user_name')
        player_rank = session.get('player_rank')
        user_info = user_name, player_rank
        return user_info
        


def check_(session=None, date=None):
    if date:
        return True
    if session and 'user_id' in session:
        return True
    print(f"Something went wrong when trying to: {check_.__name__}")
    return False 

    
def format_(date):
    formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%b-%Y')
    return formatted_date


def get_current_date_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')