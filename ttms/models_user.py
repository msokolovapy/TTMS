from flask import flash
from ttms import db,bcrypt


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

    def is_admin(self):
        return self.player_role == 'admin'
    
    def is_user(self):
        return self.player_role == 'user'
    
    def is_valid(self,password):
        if self and bcrypt.check_password_hash(self.player_password, password):
            return True
        else:
            flash('Invalid credentials, please try again.', 'danger')
    
    def is_present_in_database(self):
        if find_user_in_database_by(self.player_email_address):
            return True
        return False

class GameDayPlayer(User):
    def __init__(self,player_data):
        player_login_name,player_role,player_rank = player_data 
        super().__init__(player_login_name,None,None,None,player_role,player_rank)
        self.last_played = None
        self.player_status = 'reserve'
        self.players_played_already = []

    def __eq__(self, other):
        if isinstance(other, GameDayPlayer):
            return (self.player_login_name == other.player_login_name)

    # def get_rank(self):
    #     return self.player_rank
    
    # def get_role(self):
    #     return self.player_role

    # def get_player_login_name(self):
    #     return self.player_login_name
    
    
    def to_dict(self):
        return {
            'player_login_name': self.player_login_name,
            'player_rank': self.player_rank,
            'player_role': self.player_role,
            'last_played': self.last_played if self.last_played else None,
            'player_status': self.player_status,
            'players_played_already': self.players_played_already
        }

    @classmethod
    def from_dict(cls, data):
        player_data = (data['player_login_name'], data['player_role'], data['player_rank'])
        player = cls(player_data)
        player.last_played = data.get('last_played')
        # player.last_played = datetime.strptime(data.get('last_played'), '%Y-%m-%d %H:%M:%S') if data.get('last_played') else None
        player.player_status = data.get('player_status', 'reserve') 
        player.players_played_already = data.get('players_played_already', []) 
    
        return player

def find_user_in_database_by(player_email):
    return User.query.filter_by(player_email_address = player_email).first()

    
