#login.py
from ttms.models_match import Matches
from ttms.models_user import Players, find_user_in_database_by
from ttms.general_use_functions import redirect_to_web_page, update_session_for, obtain_info_from_webpage

def initiate_matches_and_update_session():
    players = Players()
    matches = Matches(players)
    update_session_for(players)
    update_session_for(matches)

  
def login_and_store_data():
    email, password = obtain_info_from_webpage()
    user = find_user_in_database_by(email)
    if user.is_valid(password):
        update_session_for(user)
        if user.is_admin():
            initiate_matches_and_update_session()
            return redirect_to_web_page('admin')
        if user.is_user():
            return redirect_to_web_page('users_get')
