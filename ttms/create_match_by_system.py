#create_match_by_system.py
from ttms.general_use_functions import obtain_info_from_session,obtain_info_from_webpage,\
                                        display_message_on_page, redirect_to_web_page, \
                                        update_session_for
from ttms.models_match import Match, no_more_prebooked_


def system_chooses_next_match():
    player_1_name, player_2_name = obtain_info_from_webpage()
    admin_name, matches = obtain_info_from_session()
    if no_more_prebooked_(matches):
        display_message_on_page('No more matches planned for today. \
                    Please create a match manually via Edit button', 'info')
        return redirect_to_web_page('admin', check_availability_matches = False)
    else:
        match = Match(player_1_name, player_2_name)
        matches.update_match(match,match_status = 'played',match_html_display_status = False)
        any_active_match = matches.find_specified_match(match_status = 'active', \
                                                         match_html_display_status = False)
        matches.update_match(any_active_match, \
                            match_html_display_status=True)
        update_session_for(matches)
        return redirect_to_web_page('admin')