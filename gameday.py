#gameday.py
from app import app
from sqlalchemy import cast, Float
from extensions import db
from models_booking import Booking
from models_user import User, GameDayPlayer
from models_match import Match
from datetime import datetime
import logging
import random
import sys
import json

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

            self.gameday_players.remove(admin)
            
        while len(self.gameday_players_data) > 1:
            player_login_name, player_role,player_rank = self.gameday_players_data.pop()  # Pop a player from the end
            self.gameday_players_data.sort(key=lambda x: abs(x[2] - player_rank))  # Sort based on rank difference
            closest_match = self.gameday_players_data.pop(0)  # Pop the closest match
            matched_players.append((closest_match[0], player_login_name))
        return matched_players


    def get_gameday_matches(self):
        return self.gameday_matches
   

    def find_gameday_players(self, player_1_login_name, player_2_login_name):
        lst = []
        print(player_1_login_name)
        print(player_2_login_name)
    
        for gameday_player in self.gameday_players:
            if gameday_player and (gameday_player.player_login_name in (player_1_login_name, player_2_login_name)):
                lst.append(gameday_player)
                print(gameday_player.__dict__)
    
        if len(lst) < 2:
            pass
            # logging.error('One or both gameday players not found')
        print(lst)
        return tuple(lst)


   
    def update_gameday_player(self, player_1_login_name, player_2_login_name, status=None, last_played=None):
        players_found = self.find_gameday_players(player_1_login_name, player_2_login_name)
        
        if players_found: 
            player_1, player_2 = players_found
            player_1.players_played_already.append(player_2.player_login_name)
            player_2.players_played_already.append(player_1.player_login_name) 
            
            for player in players_found:
                print('Player found')
                if status:
                    print('Attempting to edit players status')
                    setattr(player, 'player_status', status)
                    # logging.info(f'Player {player.player_login_name} status updated to {status}')
                
                if last_played:
                    print("Attempting to edit players 'last played'")
                    setattr(player, 'last_played', last_played)
                    # logging.info(f'Player {player.player_login_name} last time played and gameday_player_list updated')
                
                print(player.__dict__)

        else:
            pass
            # logging.error(f'Player duo not found. Players attributes not updated')


    def find_specified_match(self,match_to_find):
        matches_lst = self.get_gameday_matches()
        # found_matches = []
        for match in matches_lst:
            # if not match_lst: 
            #     print(f"List is empty. Updating is not possible")
            #     continue
            # for match in match_lst:
            if match == match_to_find:
                print('Match found')
                return match
        #             found_matches.append(match)
        # if found_matches:
        #     return found_matches
        # else:
            else:
                print('Match not found while find_specified_match()')
                return None


    def update_match(self,played_match,player_1_login_name, player_2_login_name):
        found_match = self.find_specified_match(match_to_find=played_match)
        if found_match:
            setattr(found_match,'player_1_login_name', player_1_login_name)
            setattr(found_match,'player_2_login_name', player_2_login_name)
        else:
            print('Match not found while update_match()')

    def update_match_status(self,played_match,match_status):
        found_match = self.find_specified_match(match_to_find=played_match)
        if found_match:
                print('Match exists prior to updating match status')
                print('Attempting to update match status...')
                setattr(found_match,'status',match_status)
                print(f'Match between {found_match.player_1_login_name} and {found_match.player_2_login_name}. Desired match status is "{match_status}. Match status updated to "{found_match.status}"')
        else:
            print('Match not found while update_match_status()')

    def create_four_matches(self):

        """Creates a list of four match objects where match.status == 'active' and match.html_display_status = True
          to load into the html template"""
        
        four_matches_list = [match_obj for match_obj in self.gameday_matches if match_obj.html_display_status]
        return four_matches_list
    
    def display_four_matches_list_details(self):
        for match in self.create_four_matches():
            print(f'Four matches list details for match between {match.player_1_login_name} and {match.player_2_login_name}')
            print(f'Match status is "{match.status}". HTML display status is "{match.html_display_status}"')

    def update_gameday_players_list(self, gameday_players_lst):
        if gameday_players_lst:
            self.gameday_players = gameday_players_lst
        else:
            logger.info('Gameday players list empty. Impossible to update')

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
        obj.gameday_players_data = [tuple(item) for item in json.loads(data['gameday_players_data'])]
        obj.gameday_players = gameday_players
        obj.gameday_matches = gameday_matches
        return obj
    

def deserialize_gameday_obj(session):
    gameday_data = session.get('gameday_object')
    gameday = GameDay.from_dict(gameday_data)
    return gameday
    
def serialize_gameday_obj(session, gameday_obj):
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



if __name__=='__main__':
    with app.app_context():
        gameday = GameDay()
        gameday.display_four_matches_list_details()
        serialized_gameday_obj = gameday.to_dict()
        print(sys.getsizeof(serialized_gameday_obj))
        print(get_deep_size(serialized_gameday_obj))
        print(serialized_gameday_obj)
        gameday_obj_restored = GameDay.from_dict(serialized_gameday_obj)



