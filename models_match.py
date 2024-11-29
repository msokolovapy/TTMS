#models_match.py

from extensions import db


class Match(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    match_start_date_time = db.Column(db.String, nullable=True)
    player_1_login_name = db.Column(db.String, nullable = False)
    player_2_login_name = db.Column(db.String, nullable = False)
    match_result = db.Column(db.String)

    def __init__(self, player_1_login_name, player_2_login_name, match_start_date_time=None, match_result=None, status = None):
        self.match_start_date_time = match_start_date_time
        self.player_1_login_name = player_1_login_name
        self.player_2_login_name = player_2_login_name
        self.match_result = match_result
        self.status = status

    def __eq__(self, other):
        if isinstance(other, Match):
            return sorted([self.player_1_login_name, self.player_2_login_name]) == sorted([other.player_1_login_name, other.player_2_login_name])
        return False


    def to_dict(self):
        return {
            'match_id': self.match_id,
            'match_start_date_time': self.match_start_date_time,
            'player_1_login_name': self.player_1_login_name,
            'player_2_login_name': self.player_2_login_name,
            'match_result': self.match_result,
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data):
        match = cls(
            player_1_login_name=data['player_1_login_name'],
            player_2_login_name=data['player_2_login_name'],
            match_start_date_time=data.get('match_start_date_time', None),
            match_result=data.get('match_result', None),
            status = data.get('status',None)
        )
        match.match_id = data.get('match_id', None)
        return match

if __name__ == '__main__':
    match1 = Match('mike','mike')
    match2 = Match('mike','jane')
    print(match1==match2)
    