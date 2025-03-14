#gameday.py
import logging
import random
import json
from flask import session
from sqlalchemy import cast, Float
from ttms import db
from ttms.models_booking import Booking
from ttms.models_user import User, GameDayPlayer
from ttms.models_match import Match
from datetime import datetime


logger = logging.getLogger(__name__)


class Players():
    def __init__(self):
        self.gameday_date = self.obtain_gameday_date()
        self.gameday_players_data = self.obtain_gameday_players_data()
        self.gameday_players = self.create_gameday_players_lst()

    def obtain_gameday_date(self):
        #find the earliest booking date >= current date
        gameday_date = db.session.query(Booking.required_booking_date)\
            .filter(Booking.required_booking_date >= datetime.today().strftime('%Y-%m-%d'))\
            .order_by(Booking.required_booking_date.asc())\
            .limit(1)\
            .scalar()
        return gameday_date

    def obtain_gameday_players_data(self):
        game_day_players_data_query_1 = db.session.query(
            Booking.player_login_name,
            User.player_role, 
            cast(User.player_rank, Float)
        ).outerjoin(User, User.player_login_name == Booking.player_login_name)\
        .filter(Booking.required_booking_date == self.gameday_date)

        game_day_players_data_query_2 = db.session.query(
            User.player_login_name,
            User.player_role,
            cast(User.player_rank, Float)
        ).filter(User.player_role == 'admin')

        combined_query = game_day_players_data_query_1.union_all(game_day_players_data_query_2)
        gameday_players_data = combined_query.all()
        return gameday_players_data


    def create_gameday_players_lst(self):
        gameday_players_data = self.obtain_gameday_players_data()
        gameday_players = [GameDayPlayer(player_data) for player_data in gameday_players_data]
        for player in gameday_players:
            player.status = 'active'
        return gameday_players


    def get_gameday_players(self):
        return self.gameday_players
    
    
    def get_gameday_players_names(self):
        return [gameday_player.player_login_name for gameday_player in self.gameday_players]
    
    def get_gameday_players_data(self):
        return self.gameday_players_data
   

    def find_gameday_players(self, player_1_login_name, player_2_login_name):
        lst = []
        for gameday_player in self.gameday_players:
            if gameday_player and (gameday_player.player_login_name in (player_1_login_name, player_2_login_name)):
                lst.append(gameday_player)
        if len(lst) < 2:
            pass
            # logging.error('One or both gameday players not found')
        return tuple(lst)

   
    def update_gameday_player(self, player_1_login_name, player_2_login_name, status=None, last_played=None):
        players_found = self.find_gameday_players(player_1_login_name, player_2_login_name)
        
        if players_found: 
            player_1, player_2 = players_found
            player_1.players_played_already.append(player_2.player_login_name)
            player_2.players_played_already.append(player_1.player_login_name) 
            
            for player in players_found:
                if status:
                    setattr(player, 'player_status', status)
                if last_played:
                    setattr(player, 'last_played', last_played)
        else:
            pass

    def sort_gameday_players(self):
        serialised_players_list = [player.to_dict() for player in self.get_gameday_players()]
        for player_dict in serialised_players_list:
            player_dict['last_played'] = datetime.strptime(player_dict['last_played'],'%Y-%m-%d %H:%M:%S') \
                                                        if player_dict['last_played'] else None
        sorted_serialised_players_list = sorted(serialised_players_list, key = lambda x: x['last_played'] if x['last_played'] else datetime(1,1,1))
        
        return sorted_serialised_players_list


    def update_gameday_players_list(self, gameday_players_lst):
        if gameday_players_lst:
            self.gameday_players = gameday_players_lst
        else:
            logger.info('Gameday players list empty. Impossible to update')

    def to_dict(self):
        return {
            'gameday_date': self.gameday_date,
            # 'gameday_players_data': json.dumps(self.gameday_players_data),
            'gameday_players': [player.to_dict() for player in self.gameday_players]}

    @classmethod
    def from_dict(cls, data):
        gameday_players = [GameDayPlayer.from_dict(player_data) for player_data in data['gameday_players']]
        obj = cls()
        obj.gameday_date = data['gameday_date']
        # obj.gameday_players_data = json.loads(data['gameday_players_data'])
        obj.gameday_players = gameday_players
        return obj

    def display_as_drop_down(self):
        sorted_serialised_players_list = self.sort_gameday_players()
        simple_player_data_list = [{'original' : player_dict['player_login_name'],
                                    'formatted' : f'{player_dict['player_login_name']} ({player_dict['player_rank']})'} 
                                    for player_dict in sorted_serialised_players_list]
        return tuple(simple_player_data_list)


def get_player_based_on_role(players_data,role):
    for player in players_data:
        if player.player_role == role:
            return player



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












