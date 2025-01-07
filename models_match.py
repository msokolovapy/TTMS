#models_match.py

from extensions import db
from elo_rating import Elo
from models_user import User
from sqlalchemy import func
import logging
import ast

logger = logging.getLogger(__name__)

class Match(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    match_start_date_time = db.Column(db.String, nullable=True)
    player_1_login_name = db.Column(db.String, nullable = False)
    player_2_login_name = db.Column(db.String, nullable = False)
    match_result = db.Column(db.String)

    def __init__(self, player_1_login_name, player_2_login_name, match_start_date_time=None, match_result=None, status = None,html_display_status = None):
        self.match_start_date_time = match_start_date_time
        self.player_1_login_name = player_1_login_name
        self.player_2_login_name = player_2_login_name
        self.match_result = match_result
        self.status = status
        self.html_display_status = html_display_status

    def __eq__(self, other):
        if isinstance(other, Match):
            try:
                return sorted([self.player_1_login_name, self.player_2_login_name]) == sorted([other.player_1_login_name, other.player_2_login_name])
            except Exception as e:
                print(f'Exception while trying to match found == match is {e}')
        else:
            print(f'match object is not an instance of Match class')
            return False



    def convert_match_result_to_integer(self):
        if self.match_result:
            match_result = ast.literal_eval(self.match_result)
            return tuple([tuple(map(int, score_duo)) for score_duo in match_result])
        else:
            logger.info("Match result doesn't exist. Impossible to convert to tuple")

    def determine_match_winner(self):
        match_result = self.convert_match_result_to_integer()
        games_won_by_player_1 = sum(1 for score_duo in match_result if score_duo[0] > score_duo[1])
        games_won_by_player_2 = sum(1 for score_duo in match_result if score_duo[1] > score_duo[0]) 
     
        if games_won_by_player_1 > games_won_by_player_2:  
            return self.player_1_login_name, self.player_2_login_name
        else:
            return self.player_2_login_name, self.player_1_login_name                

    def extract_current_player_rank(self):
        winner_name, loser_name = self.determine_match_winner()
        winner = User.query.filter_by(player_login_name=winner_name).first()
        loser = User.query.filter_by(player_login_name=loser_name).first()
        return winner.player_rank, loser.player_rank


    def update_player_ranking(self):
        winner_rank, loser_rank = self.extract_current_player_rank()
        return calculate_elo(winner_rank,loser_rank)



    def to_dict(self):
        return {
            'match_id': self.match_id,
            'match_start_date_time': self.match_start_date_time,
            'player_1_login_name': self.player_1_login_name,
            'player_2_login_name': self.player_2_login_name,
            'match_result': self.match_result,
            'status': self.status,
            'html_display_status': self.html_display_status
        }

    @classmethod
    def from_dict(cls, data):
        match = cls(
            player_1_login_name=data['player_1_login_name'],
            player_2_login_name=data['player_2_login_name'],
            match_start_date_time=data.get('match_start_date_time', None),
            match_result=data.get('match_result', None),
            status = data.get('status',None),
            html_display_status = data.get('html_display_status',None)
        )
        match.match_id = data.get('match_id', None)
        return match

def retrieve_match_data(today_date):
    match_obj_list = db.session.query(
    Match).filter(func.date(Match.match_start_date_time) == today_date).all()
    logger.info(f"Retrieved match data for {today_date}")
    if match_obj_list:
        return match_obj_list
    else:
        logger.info(f'No match data found')

def calculate_elo(winner_rating, loser_rating, k_factor=32):
    """
    Calculate updated Elo ratings for winner and loser.
    
    Parameters:
    - winner_rating (float): Current Elo rating of the winner.
    - loser_rating (float): Current Elo rating of the loser.
    - k_factor (int): K-factor that controls the adjustment size. Default is 32.
    
    Returns:
    - tuple: Updated ratings for the winner and loser (winner_new_rating, loser_new_rating).
    """
    
    expected_winner_score = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser_score = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    
    actual_winner_score = 1
    actual_loser_score = 0
    
    winner_new_rating = winner_rating + k_factor * (actual_winner_score - expected_winner_score)
    loser_new_rating = loser_rating + k_factor * (actual_loser_score - expected_loser_score)
    
    return round(winner_new_rating, 2), round(loser_new_rating, 2)


if __name__ == '__main__':
    match1 = Match('mike','mike')
    match2 = Match('mike','jane')
    print(match1==match2)
    