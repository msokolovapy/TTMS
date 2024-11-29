import sys
import os
from app import app, db
from models import User,Match,Booking
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt

# Add the project directory to the Python path
# sys.path.append(os.path.abspath('C:/Users/maria/Desktop/New_folder/TTMS'))

# Use the application context
with app.app_context():
    # Clear all records from the booking table
    # db.session.query(User).delete()

    # # Commit the changes to the database
    # db.session.commit()

    bcrypt = Bcrypt()

    # Add users to the user table one by one to ensure password hashing
    users = [
        {'player_login_name': 'john', 'player_phone_number': '415263563', 'player_email_address': 'email1@gmail.com', 'player_password': '123a', 'player_role': 'admin', 'player_rank': 3},
        {'player_login_name': 'jane', 'player_phone_number': '412365489', 'player_email_address': 'email2@gmail.com', 'player_password': '124b', 'player_role': 'user', 'player_rank': 3},
        {'player_login_name': 'nick', 'player_phone_number': '478523215', 'player_email_address': 'email3@gmail.com', 'player_password': '125a', 'player_role': 'user', 'player_rank': 3},
        {'player_login_name': 'mike', 'player_phone_number': '459867521', 'player_email_address': 'email4@gmail.com', 'player_password': '126b', 'player_role': 'user', 'player_rank': 3},
        {'player_login_name': 'robert', 'player_phone_number': '413125654', 'player_email_address': 'email5@gmail.com', 'player_password': '127a', 'player_role': 'user', 'player_rank': 6},
        {'player_login_name': 'bill', 'player_phone_number': '415192356', 'player_email_address': 'email6@gmail.com', 'player_password': '128b', 'player_role': 'user', 'player_rank': 6},
        {'player_login_name': 'sarah', 'player_phone_number': '417892364', 'player_email_address': 'email7@gmail.com', 'player_password': '129a', 'player_role': 'user', 'player_rank': 6},
        {'player_login_name': 'fiona', 'player_phone_number': '422635599', 'player_email_address': 'email8@gmail.com', 'player_password': '130b', 'player_role': 'user', 'player_rank': 6},
        {'player_login_name': 'james', 'player_phone_number': '477829345', 'player_email_address': 'email9@gmail.com', 'player_password': '131a', 'player_role': 'user', 'player_rank': 12},
        {'player_login_name': 'jojo', 'player_phone_number': '415698798', 'player_email_address': 'email10@gmail.com', 'player_password': '132b', 'player_role': 'user', 'player_rank': 12},
        {'player_login_name': 'meredith', 'player_phone_number': '477326596', 'player_email_address': 'email11@gmail.com', 'player_password': '133a', 'player_role': 'user', 'player_rank': 12},
        {'player_login_name': 'momo', 'player_phone_number': '418963321', 'player_email_address': 'email12@gmail.com', 'player_password': '134b', 'player_role': 'user', 'player_rank': 12}
    ]

    for user_data in users:
        user = User(
            player_login_name=user_data['player_login_name'],
            player_phone_number=user_data['player_phone_number'],
            player_email_address=user_data['player_email_address'],
            player_password=user_data['player_password'],  # Password will be hashed in the __init__ method
            player_role=user_data['player_role'],
            player_rank=user_data['player_rank']
        )
        db.session.add(user)

    db.session.commit()


    

