#gameday.py
import logging
import random
import sys
import json
from flask import session
from sqlalchemy import cast, Float
from ttms import db
from ttms.models_booking import Booking
from ttms.models_user import User, GameDayPlayer
from ttms.models_match import Match
from datetime import datetime


logger = logging.getLogger(__name__)


class GameDay():
    def __init__(self):
        self.gameday_date = self.obtain_gameday_date()
        self.gameday_players_data = self.obtain_gameday_players_data()
        self.gameday_players = self.create_gameday_players_lst()
        self.gameday_matches = self.create_gameday_match_lst()
        

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

    def create_gameday_match_lst(self):
            matched_duos = self.match_players()
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

    def get_player_based_on_role(self, role):
        for player in self.gameday_players:
            if player.player_role == role:
                return player

        
    def match_players(self):
        """ Matches players based on the closest rank number"

            Outputs list of player names in tuple"""
        
        matched_players = []
        random.shuffle(self.gameday_players_data)
        if len(self.gameday_players_data) % 2 != 0: #odd number of players, admin needs to be popped off list
            admin = self.get_player_based_on_role(role = 'admin')

            self.gameday_players_data = [player for player in self.gameday_players_data 
                             if not (player[0] == admin.player_login_name and 
                                     player[1] == admin.player_role and 
                                     player[2] == admin.player_rank)]

            # self.gameday_players.remove(admin)
            
        while len(self.gameday_players_data) > 1:
            player_login_name, player_role,player_rank = self.gameday_players_data.pop()  # Pop a player from the end
            self.gameday_players_data.sort(key=lambda x: abs(x[2] - player_rank))  # Sort based on rank difference
            closest_match = self.gameday_players_data.pop(0)  # Pop the closest match
            matched_players.append((closest_match[0], player_login_name))
        return matched_players


    def get_gameday_matches(self):
        return self.gameday_matches
    
    def get_gameday_players(self):
        return self.gameday_players
    
    
    def get_gameday_players_names(self):
        return [gameday_player.player_login_name for gameday_player in self.gameday_players]
   

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
    

    def update_gameday_players_list(self, gameday_players_lst):
        if gameday_players_lst:
            self.gameday_players = gameday_players_lst
        else:
            logger.info('Gameday players list empty. Impossible to update')

    def counter_active_matches(self):
        counter = sum(1 for match in self.gameday_matches if match.status == 'active' and not match.html_display_status)
        return counter
    
    def display_gameday_players_data(self):
        print("{:<20} {:<10} {:<10}".format(
                            "Player Name", 
                            "Player Role", 
                            "Player Rank", 
                        ))
        print(50*'=')
        if not self.gameday_players_data:
            print('No player data found')
        for player_data in self.gameday_players_data:
            player_login_name, player_role, player_rank = player_data
            print("{:<20} {:<10} {:<10}".format(
                            player_login_name, 
                            player_role, 
                            player_rank, 
                        ))
    

    def to_dict(self):
        return {
            'gameday_date': self.gameday_date,
            'gameday_players_data': json.dumps(self.gameday_players_data),
            'gameday_players': [player.to_dict() for player in self.gameday_players], 
            'gameday_matches': [match.to_dict() for match in self.gameday_matches],  
                }

    @classmethod
    def from_dict(cls, data):
        gameday_players = [GameDayPlayer.from_dict(player_data) for player_data in data['gameday_players']]
        gameday_matches = [Match.from_dict(match_data) for match_data in data['gameday_matches']]
        obj = cls()
        obj.gameday_date = data['gameday_date']
        obj.gameday_players_data = json.loads(data['gameday_players_data'])
        obj.gameday_players = gameday_players
        obj.gameday_matches = gameday_matches
        return obj
    

def deserialize_gameday_obj():
    gameday_data = session.get('gameday_object')
    gameday = GameDay.from_dict(gameday_data)
    return gameday
    
def serialize_gameday_obj(gameday_obj):
    session['gameday_object'] = gameday_obj.to_dict()


def get_deep_size(obj, seen=None):
    """ Recursively calculates the total memory size of an object and its contents. """
    if seen is None:
        seen = set()
    
    obj_id = id(obj)
    if obj_id in seen:
        return 0  # Avoid counting the same object twice
    
    seen.add(obj_id)
    
    size = sys.getsizeof(obj)  # Get the size of the object itself
    
    if isinstance(obj, dict):
        # Add size of keys and values
        size += sum(get_deep_size(k, seen) + get_deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set)):
        # Add size of each item
        size += sum(get_deep_size(i, seen) for i in obj)
    
    return size

def create_drop_down_list(sorted_serialised_players_list):
    simple_player_data_list = [{'original' : player_dict['player_login_name'],
                                'formatted' : f'{player_dict['player_login_name']} ({player_dict['player_rank']})'} 
                                for player_dict in sorted_serialised_players_list]
    return tuple(simple_player_data_list)

def display_gameday_matches(matches_list):
    for index,match in enumerate(matches_list):
        print("{:<10} {:<20} {:<20} {:<10} {:<10}".format(
            f'Match {index + 1}',match.player_1_login_name, 
                                match.player_2_login_name,
                                match.status,
                                match.html_display_status))