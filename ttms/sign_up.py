#sign_up.py
from flask import request, render_template
from ttms import db,bcrypt
from ttms.login import display_message_on_page,redirect_to_web_page
from ttms.models_user import find_user_in_database_by,User



def update_database_for(object):
    add_to_database_session(object)
    write_to_database()

def add_to_database_session(object):
    return db.session.add(object)

def write_to_database():
    return db.session.commit()

    
def create_user(user_info):
    user = User(player_login_name=user_info['user_name'],
            player_email_address=user_info['user_email'],
            player_phone_number=user_info['user_phone_number'],
            player_password=bcrypt.generate_password_hash(user_info['user_password']).decode('utf-8'),
            player_role='user',
            player_rank=1500
        )
    return user

def build_web_page(html_template, **kwargs):
    html_template += '.html'
    return render_template(html_template, **kwargs)



def obtain_player_info_from_signup_page():
        signup_data = {'user_name':request.form['nickname'],
                       'user_email':request.form['email'],
                        'user_phone_number':request.form['phone'],
                        'user_password':request.form['password']}
        return signup_data


def signup_user():
    signup_data = obtain_player_info_from_signup_page()
    user = create_user(signup_data)
    if user.is_present_in_database():  
       display_message_on_page('User details already in database. Please login instead.', 'danger')
       return redirect_to_web_page('login')
    update_database_for(user)
    display_message_on_page("You've successfully joined our family of amazing table tennis players! Please login below",'success')
    return redirect_to_web_page('login')
