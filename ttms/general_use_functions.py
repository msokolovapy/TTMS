#general_use_functions.py
from datetime import datetime
from flask import render_template, redirect, url_for, session, flash, request

from ttms import db
from ttms.models_match import Matches, deserialize_, get_match_results
from ttms.models_user import Players, User



def update_database_for(object):
    add_to_database_session(object)
    write_to_database()

def add_to_database_session(object):
    return db.session.add(object)

def write_to_database():
    return db.session.commit()

def convert_to_boolean(string):
   if string == 'True':
      return True
   return False


def build_web_page(html_file_name,user_name = None,four_matches_list = None,check_availability_matches = None,drop_down_list = None):
    html_file_name += '.html'
    try:
        return render_template(html_file_name, user_name=user_name, 
                                four_matches_list=four_matches_list, 
                                check_availability_matches = check_availability_matches,
                                drop_down_list = drop_down_list)
    except Exception as e:
        return render_template('error.html') 


def redirect_to_web_page(html_file_name,check_availability_matches = True):
    try:
        return redirect(url_for(html_file_name, check_availability_matches = check_availability_matches))
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
    print(function_name)
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
         print(f'print function_name again:{function_name}')
         match_data = {
                  'match_start_date_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  'player_1_login_name' : request.form.get('player1_login_name'),
                  'player_2_login_name' : request.form.get('player2_login_name'),
                  'match_result' : get_match_results(),
                  }
         player_data = match_data['player_1_login_name'], match_data['player_2_login_name']
         time_last_played = match_data['match_start_date_time']
         print(match_data, player_data, time_last_played, sep = '\n')
         return match_data, player_data, time_last_played
    elif function_name == 'create_match_by_system':
        player_1_login_name = request.form.get('player_1_login_name')
        player_2_login_name = request.form.get('player_2_login_name') 
        return player_1_login_name, player_2_login_name      


def obtain_info_from_session():
    function_name = request.endpoint
    if function_name in ('admin','create_match_by_system'):
        name = session.get('user_name')
        matches = deserialize_('matches')
        return name, matches 
    elif function_name == 'submit_match_results':
        matches = deserialize_('matches')
        players = deserialize_('players')
        return matches, players
    elif function_name == 'create_match_manually':   
        players = deserialize_('players')
        matches = deserialize_('matches')
        return players, matches