#login.py
from flask import render_template, redirect,flash,url_for,session, request
from ttms.gameday import GameDay
from ttms.models_user import find_user_in_database_by

def build_web_page(html_file_name):
    html_file_name += '.html'
    try:
        return render_template(html_file_name)
    except Exception:
        return render_template('error_page.html') 

def redirect_to_web_page(html_file_name):
    try:
        return redirect(url_for(html_file_name))
    except Exception:
        return render_template('error_page.html')


def display_message_on_page(message_str, message_type):
    flash(message_str,message_type)

def initiate_matches():
    return GameDay()

def initiate_matches_and_update_session():
    gameday_data = initiate_matches()
    return update_session(gameday_data = gameday_data)

  
def update_session(user = None, gameday_data = None):
     if user:
          session['user_id'] = user.player_id
          session['user_role'] = user.player_role
          session['user_name'] = user.player_login_name
          session['player_rank'] = user.player_rank
     elif gameday_data:
        session['gameday_object'] = gameday_data.to_dict()  
      


def obtain_player_info_from_login_page(request):
        player_email = request.form['player_email']
        password = request.form['password']
        return player_email, password
    

def login_and_store_data():
    user_email, user_password = obtain_player_info_from_login_page(request)
    user = find_user_in_database_by(user_email)
    if user.is_valid(user_password):
        update_session(user = user)
        if user.is_admin():
            initiate_matches_and_update_session()
            return redirect_to_web_page('admin')
        if user.is_user():
            return redirect_to_web_page('user')
