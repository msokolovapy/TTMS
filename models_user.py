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

    def get_rank(self):
        return self.player_rank

    def get_player_login_name(self):
        return self.player_login_name
    
    def to_dict(self):
        return {
            'player_login_name' : self.player_login_name,
            'player_rank' : self.player_rank,
            'player_role': self.player_role,
            'last_played': self.last_played,
            'player_status': self.player_status,
            'players_played_already': self.players_played_already
        }

    @classmethod
    def from_dict(cls, data):
        player_data = (data['player_login_name'], data['player_role'], data['player_rank'])
        player = cls(player_data)
        player.last_played = data.get('last_played', None) 
        player.player_status = data.get('player_status', 'reserve') 
        player.players_played_already = data.get('players_played_already', [])  
        return player

if __name__ == '__main__':
    pass
    
