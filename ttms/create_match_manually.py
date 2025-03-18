#create_match_manually.py
from flask import request, session
from datetime import datetime
from ttms.models_match import Match, get_match_results
from ttms.gameday import deserialize_
from ttms.login import build_web_page,redirect_to_web_page, update_session_for



def obtain_user_input_for(function_name):
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
    elif function_name == 'submit_match_results':
        pass
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

def obtain_info_from_session_for(function_name):
    if function_name == 'admin':
        name = session.get('user_name')
        matches = deserialize_('matches')
        return name, matches 
    elif function_name == 'create_match_manually':   
        players = deserialize_('players')
        matches = deserialize_('matches')
        return players, matches
          
def choose_players_and_create_match_manually():
    players, matches = obtain_info_from_session_for('create_match_manually')
    names = obtain_user_input_for('create_match_manually')
    if names:
        old_name_1, old_name_2, selected_name_1, selected_name_2 = names
        old_match = Match(old_name_1, old_name_2)
        matches.update_match(old_match, selected_name_1, selected_name_2, match_status = 'active')
        update_session_for(matches)
        return redirect_to_web_page('admin')
    return build_web_page('admin_create_match_manually', drop_down_list = players.display_as_drop_down())








