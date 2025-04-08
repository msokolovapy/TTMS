from ttms.models_match import create_match_using_
from ttms.general_use_functions import obtain_info_from_webpage, obtain_info_from_session,\
                                        update_session_for, update_database_for, redirect_to_web_page




def update_match_player_session(played_match, player_data, time_last_played):
    player_1_login_name, player_2_login_name = player_data
    matches, players = obtain_info_from_session()
    matches.update_match(played_match, match_status = 'played')
    players.update_gameday_player(player_1_login_name, 
                                  player_2_login_name, 
                                  'reserve', 
                                  time_last_played)
    update_session_for(matches)
    update_session_for(players)


def obtain_match_results_and_update_session():
    match_data,player_data,time_last_played = obtain_info_from_webpage()
    played_match = create_match_using_(match_data)
    update_match_player_session(played_match, player_data, time_last_played)
    update_database_for(played_match)
    return redirect_to_web_page('admin')


