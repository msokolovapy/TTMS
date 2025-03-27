#create_match_manually.py

from ttms.models_match import Match
from ttms.general_use_functions import obtain_info_from_session, obtain_info_from_webpage,\
                                        update_session_for, redirect_to_web_page, \
                                        build_web_page

          
def choose_players_and_create_match_manually():
    matches,players = obtain_info_from_session()
    names = obtain_info_from_webpage()
    if names:
        old_name_1, old_name_2, selected_name_1, selected_name_2 = names
        old_match = Match(old_name_1, old_name_2)
        matches.update_match(old_match, selected_name_1, selected_name_2, match_status = 'active')
        update_session_for(matches)
        return redirect_to_web_page('admin')
    return build_web_page('admin_create_match_manually', drop_down_list = players.display_as_drop_down())








