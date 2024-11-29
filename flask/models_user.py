from extensions import db


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
        self.player_password = player_password
        self.player_role = player_role
        self.player_rank = player_rank


