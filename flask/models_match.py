#models_match.py
from extensions import db

class Match(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    match_start_date_time = db.Column(db.String, nullable=True)
    player_1_login_name = db.Column(db.String, nullable = False)
    player_2_login_name = db.Column(db.String, nullable = False)
    match_result = db.Column(db.String)

    def __init__(self, player_1_login_name, player_2_login_name, match_start_date_time=None, match_result=None):
        self.match_start_date_time = match_start_date_time
        self.player_1_login_name = player_1_login_name
        self.player_2_login_name = player_2_login_name
        self.match_result = match_result