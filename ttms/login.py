#login.py
from flask import render_template, redirect,flash,url_for,session, request
from ttms.gameday import Matches, Players
from ttms.models_user import User
from ttms.models_user import find_user_in_database_by

def build_web_page(html_file_name,user_name = None,four_matches_list = None):
    html_file_name += '.html'
    try:
        return render_template(html_file_name, user_name=user_name, four_matches_list=four_matches_list)
    except Exception:
        return render_template('error.html') 


def redirect_to_web_page(html_file_name):
    try:
        return redirect(url_for(html_file_name))
    except Exception:
        return render_template('error.html')


def display_message_on_page(message_str, message_type):
    flash(message_str,message_type)



def initiate_matches_and_update_session():
    players = Players()
    matches = Matches(players)
    update_session_for(players)
    update_session_for(matches)


  
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
      


def obtain_player_info_from_login_page():
        player_email = request.form['player_email']
        password = request.form['password']
        return player_email, password
    

def login_and_store_data():
    email, password = obtain_player_info_from_login_page()
    user = find_user_in_database_by(email)
    if user.is_valid(password):
        update_session_for(user)
        if user.is_admin():
            initiate_matches_and_update_session()
            return redirect_to_web_page('admin')
        if user.is_user():
            return redirect_to_web_page('users')
