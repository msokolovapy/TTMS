#sign_up.py
from ttms.general_use_functions import update_database_for, display_message_on_page,\
                                       redirect_to_web_page, obtain_info_from_webpage
from ttms.models_user import create_user_from


def signup_user():
    signup_data = obtain_info_from_webpage()
    user = create_user_from(signup_data)
    if user.is_present_in_database():  
       display_message_on_page('User details already in database. Please login instead.', 'danger')
       return redirect_to_web_page('login')
    update_database_for(user)
    display_message_on_page("You've successfully joined our family of amazing table tennis players! Please login below",'success')
    return redirect_to_web_page('login')
