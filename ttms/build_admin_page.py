#build_admin_page.py
from flask import session
from ttms.gameday import deserialize_gameday_obj

def user_is(role):
   if session.get('user_role') == role:
       return True
   return False

def user_is_logged_in():
   if 'user_id' in session:
       return True
   return False

def login_checks_pass():
   if user_is_logged_in() and user_is('admin'):
       return True
   return False

def obtain_info_from_(session):
   name = session.get('user_name')
   matches = deserialize_gameday_obj()
   return name, matches

