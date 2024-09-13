from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    player_id = db.Column(db.Integer, primary_key=True)
    player_login_name = db.Column(db.String, nullable=False, unique=True)
    player_phone_number = db.Column(db.String, nullable=False)
    player_email_address = db.Column(db.String, nullable=False, unique=True)
    player_password = db.Column(db.String, nullable=False)
    player_role = db.Column(db.String, nullable=False)
    player_rank = db.Column(db.Float,nullable=False)

    def __init__(self, player_login_name,player_phone_number,player_email_address,player_password,player_role,player_rank):
        self.player_login_name = player_login_name
        self.player_phone_number = player_phone_number
        self.player_email_address = player_email_address
        self.player_password = bcrypt.generate_password_hash(player_password).decode('utf-8')
        self.player_role = player_role
        self.player_rank = player_rank


class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    booking_day_time = db.Column(db.String, nullable=False)
    player_1_login_name = db.Column(db.String, nullable = False)
    player_2_login_name = db.Column(db.String, nullable = False)
    booking_payment_status = db.Column(db.Integer)

    def __init__(self, booking_day_time, player_1_login_name, player_2_login_name,booking_payment_status):
        self.booking_day_time = booking_day_time
        self.player_1_login_name = player_1_login_name
        self.player_2_login_name = player_2_login_name
        self.booking_payment_status = booking_payment_status


class Match(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    match_start_date_time = db.Column(db.String, nullable=False)
    player_1_login_name = db.Column(db.String, nullable = False)
    player_2_login_name = db.Column(db.String, nullable = False)
    match_result = db.Column(db.String)

    def __init__(self, match_id, match_start_date_time,player_1_login_name, player_2_login_name,match_result):
        self.match_start_date_time = match_start_date_time
        self.player_1_login_name = player_1_login_name
        self.player_2_login_name = player_2_login_name
        self.match_result = match_result
