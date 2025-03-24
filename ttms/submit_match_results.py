from datetime import datetime
from flask import request
from ttms.models_match import get_match_results
from ttms.login import update_session_for,redirect_to_web_page
from ttms.sign_up import update_database_for
from ttms.gameday import deserialize_
from ttms.models_match import Match




def update_session(played_match, player_data, time_last_played):
    player_1_login_name, player_2_login_name = player_data
    matches = deserialize_('matches')
    players = deserialize_('players')
    matches.update_match(played_match, match_status = 'played')
    players.update_gameday_player(player_1_login_name, 
                                  player_2_login_name, 
                                  'reserve', 
                                  time_last_played)
    update_session_for(matches)
    update_session_for(players)


def create_match_using_(match_data):
    new_match = Match(
        match_start_date_time = match_data['match_start_date_time'],
        player_1_login_name = match_data['player_1_login_name'],
        player_2_login_name = match_data['player_2_login_name'],
        match_result = match_data['match_result']
                      )
    return new_match

def obtain_match_data_from_submit_results_page():
    match_data = {
                  'match_start_date_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  'player_1_login_name' : request.form.get('player1_login_name'),
                  'player_2_login_name' : request.form.get('player2_login_name'),
                  'match_result' : get_match_results(),
                  }
    player_data = match_data['player_1_login_name'], match_data['player_2_login_name']
    time_last_played = match_data['match_start_date_time']
    return match_data, player_data, time_last_played


def obtain_match_results_and_update_session():
    match_data,player_data,time_last_played = obtain_match_data_from_submit_results_page()
    played_match = create_match_using_(match_data)
    update_session(played_match, player_data, time_last_played)
    update_database_for(played_match)
    return redirect_to_web_page('admin', check_availability_matches=True)


