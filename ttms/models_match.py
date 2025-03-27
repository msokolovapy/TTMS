#models_match.py
import random
from flask import session
from sqlalchemy import func
import ast

from ttms import db
from ttms.models_user import User, get_player_based_on_role, Players


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
            print("Match result doesn't exist. Impossible to convert to tuple")

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
    print(f"Retrieved match data for {today_date}")
    if match_obj_list:
        return match_obj_list
    else:
        print(f'No match data found')

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

def get_match_results():
    """This function obtains individual scores of two players from a form and 
       writes game scores as a list of tuples
    """
    from flask import request
    game_results = []
    for i in range(1, 6):
        game1_score = request.form.get(f'player1_game_{i}')
        game2_score = request.form.get(f'player2_game_{i}')
        if game1_score and game2_score:
            game_results.append((game1_score, game2_score))
    
    return str(tuple(game_results))

def create_match_using_(match_data):
    new_match = Match(
        match_start_date_time = match_data['match_start_date_time'],
        player_1_login_name = match_data['player_1_login_name'],
        player_2_login_name = match_data['player_2_login_name'],
        match_result = match_data['match_result']
                      )
    return new_match

def no_more_prebooked_(matches):
    counter_active_matches = matches.counter_active_matches()
    if counter_active_matches == 0:
        return True
    return False



class Matches():
    def __init__(self, players = None):
        if players:
            self.gameday_matches = create_gameday_match_lst(players)
        else:
            self.gameday_matches = []
        
    def get_gameday_matches(self):
        return self.gameday_matches

    def find_specified_match(self, match_to_find=None,
                             match_status=None, 
                             match_html_display_status=None):
            matches_list = self.get_gameday_matches()

            if not matches_list:
                raise ValueError('Match list is empty')
            
            #finds specific match:
            if match_to_find is not None:
                for match in matches_list:
                    if match == match_to_find:
                        return match
                return None
            
            #finds any match that satisfies any of below criteria:
            if match_status is not None and match_html_display_status is not None:
                for match in matches_list:
                    if match.status == match_status and match.html_display_status == match_html_display_status:
                        return match
                return None

            if match_status is not None:
                for match in matches_list:
                    if match.status == match_status:
                        return match
                return False  

            if match_html_display_status is not None:
                for match in matches_list:
                    if match.html_display_status == match_html_display_status:
                        return match
                return False 

            return None
    

    def update_match(self, match_to_update, player_1_login_name=None, 
                          player_2_login_name=None, match_status=None, 
                          match_html_display_status=None):
        found_match = self.find_specified_match(match_to_find=match_to_update)
        
        if not found_match:
            raise ValueError('Match not found while update_match()')

        if player_1_login_name is not None and player_2_login_name is not None:
            setattr(found_match, 'player_1_login_name', player_1_login_name)
            setattr(found_match, 'player_2_login_name', player_2_login_name)

        if match_status is not None and match_html_display_status is not None:
            setattr(found_match, 'status', match_status)
            setattr(found_match, 'html_display_status', match_html_display_status)
            
        if match_status is not None:
            setattr(found_match, 'status', match_status)

        if match_html_display_status is not None:
            setattr(found_match, 'html_display_status', match_html_display_status)

        return None

    def to_display(self):
        """Creates a list of four match objects where match.status == 'active' and match.html_display_status = True
          to load into the html template"""
        four_matches_list = [match_obj for match_obj in self.gameday_matches if match_obj.html_display_status]
        return four_matches_list
 
    def counter_active_matches(self):
        counter = sum(1 for match in self.gameday_matches if match.status == 'active' and not match.html_display_status)
        return counter
   

    def to_dict(self):
        return {
            'gameday_matches': [match.to_dict() for match in self.gameday_matches],  
                }

    @classmethod
    def from_dict(cls, data):
        gameday_matches = [Match.from_dict(match_data) for match_data in data['gameday_matches']]
        obj = cls()
        obj.gameday_matches = gameday_matches
        return obj


def create_gameday_match_lst(players):
        matched_duos = match_players(players)
        num_matches_to_display = min(len(matched_duos), 4)
        random_indexes = random.sample(range(len(matched_duos)), num_matches_to_display)
        match_lst = []
        for i,matched_duo in enumerate(matched_duos):
            player_1_login_name, player_2_login_name = matched_duo
            match = Match(player_1_login_name=player_1_login_name, player_2_login_name=player_2_login_name)
            match.status = 'active'
            if i in random_indexes:
                match.html_display_status = True
            else:
                match.html_display_status = False
            match_lst.append(match)
        return match_lst

        
def match_players(players):
    """ Matches players based on the closest rank number"
        Outputs list of player names in tuple"""
    matched_players = []
    players_data = players.get_gameday_players_data()
    random.shuffle(players_data)
    if len(players_data) % 2 != 0: #odd number of players, admin needs to be popped off list
        admin = get_player_based_on_role(players_data,'admin')

        players_data = [player for player in players_data 
                            if not (player[0] == admin.player_login_name and 
                                    player[1] == admin.player_role and 
                                    player[2] == admin.player_rank)]
    players_data = players_data.copy()   
    while len(players_data) > 1:
        player_login_name, player_role,player_rank = players_data.pop()  # Pop a player from the end
        players_data.sort(key=lambda x: abs(x[2] - player_rank))  # Sort based on rank difference
        closest_match = players_data.pop(0)  # Pop the closest match
        matched_players.append((closest_match[0], player_login_name))
    return matched_players   


def deserialize_(data):
    if data == 'matches':
        matches_data = session.get('matches')
        matches = Matches.from_dict(matches_data)
        return matches
    if data == 'players':
        players_data = session.get('players')
        players = Players.from_dict(players_data)
        return players
    
    
def serialize_(obj):
    if isinstance(obj,Matches):
        session['matches'] = obj.to_dict()
    elif isinstance(obj,Players):
        session['players'] = obj.to_dict()

