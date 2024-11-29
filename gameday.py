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




class GameDay():
    def __init__(self,substitute_player):
        self.substitute_player = substitute_player
        self.game_day_date = self.obtain_game_day_date()
        self.game_day_players_data = self.obtain_game_day_players_data()
        self.gameday_players = self.create_gameday_players_lst()
        self.gameday_matches = self.create_gameday_match_lst()
        self.four_matches_list = self.create_four_matches()

    def obtain_game_day_date(self):
        #find the earliest booking date >= current date
        game_day_date = db.session.query(Booking.required_booking_date)\
            .filter(Booking.required_booking_date >= datetime.today().strftime('%Y-%m-%d'))\
            .order_by(Booking.required_booking_date.asc())\
            .limit(1)\
            .scalar()
        return game_day_date

    def obtain_game_day_players_data(self):
        game_day_players_data = db.session.query(
            Booking.player_login_name, 
            cast(User.player_rank,Float)
            ).outerjoin(User, User.player_login_name == Booking.player_login_name)\
            .filter(Booking.required_booking_date == self.game_day_date)\
            .all()
        return game_day_players_data

    def create_gameday_players_lst(self):
        gameday_players = [GameDayPlayer(player_data) for player_data in self.game_day_players_data]
        for player in gameday_players:
            player.status = 'active'
        return gameday_players

    def create_gameday_match_lst(self):
        matched_duos = self.match_players()
        match_lst = []
        for matched_duo in matched_duos:
            player_1_login_name, player_2_login_name = matched_duo
            match = Match(player_1_login_name=player_1_login_name, player_2_login_name=player_2_login_name)
            match.status = 'active'
            match_lst.append(match)
        return match_lst

        
    def match_players(self):
        game_day_players_data = self.game_day_players_data.copy()
        matched_players = []
        random.shuffle(game_day_players_data)
        if len(game_day_players_data) % 2 != 0: #odd number of players, one players randomly popped off list and matched with admin
            random_index = random.randint(0, len(game_day_players_data) - 1)
            player_login_name = game_day_players_data.pop(random_index)[0]
            matched_players.append([self.substitute_player,player_login_name])
        while len(game_day_players_data) > 1:
            player_login_name, player_rank = game_day_players_data.pop()  # Pop a player from the end
            game_day_players_data.sort(key=lambda x: abs(x[1] - player_rank))  # Sort based on rank difference
            closest_match = game_day_players_data.pop(0)  # Pop the closest match
            matched_players.append((closest_match[0], player_login_name))
        return matched_players


    def create_four_matches(self):
        random.shuffle(self.gameday_matches) #provides randomly shuffled gameday.gameday_matches list
        four_matches_list = self.gameday_matches[:4] # provides first four match objects
        return four_matches_list

    def get_gameday_matches(self):
        return self.gameday_matches

    def get_four_matches_list(self):
        return self.four_matches_list
   

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
            
            for player in players_found:
                print('Player found')
                if status:
                    print('Attempting to edit players status')
                    setattr(player, 'player_status', status)
                    # logging.info(f'Player {player.player_login_name} status updated to {status}')
                
                if last_played:
                    print("Attempting to edit players 'last played'")
                    player_1.players_played_already.append(player_2.player_login_name)
                    player_2.players_played_already.append(player_1.player_login_name)
                    setattr(player, 'last_played', last_played)
                    # logging.info(f'Player {player.player_login_name} last time played and gameday_player_list updated')
                print(player.__dict__)
        else:
            pass
            # logging.error(f'Player duo not found. Players attributes not updated')


    def find_specified_match(self,match_to_find):
        matches_lst = [self.get_four_matches_list(),self.get_gameday_matches()]
        for match_lst in matches_lst:
            if not match_lst: 
                print(f"List is empty. Updating is not possible")
                continue
            for match in match_lst:
                if match == match_to_find:
                    print('Match found')
                    return match


    def update_match(self,played_match,player_1_login_name, player_2_login_name):
        match = self.find_specified_match(match_to_find=played_match)
        if match:
            setattr(match,'player_1_login_name', player_1_login_name)
            setattr(match,'player_2_login_name', player_2_login_name)
        return

    def update_match_status(self,played_match,match_status):
        match = self.find_specified_match(match_to_find=played_match)
        if match:
            print('Match exists prior to updating match status')
            print('Attempting to update match status...')
            setattr(match,'status',match_status)
            print(f'Match between {match.player_1_login_name} and {match.player_2_login_name}. Desired match status is "{match_status}. Match status updated to "{match.status}"')
        else:
            print('error here')
    
    def display_four_matches_list_details(self):
        for match in self.four_matches_list:
            print(f'Four matches list details for match between {match.player_1_login_name} and {match.player_2_login_name}')
            print(f'Match status is "{match.status}"')

    def to_dict(self):
        return {
            'substitute_player': self.substitute_player,
            'game_day_date': self.game_day_date,  
            'gameday_players': [player.to_dict() for player in self.gameday_players], 
            'gameday_matches': [match.to_dict() for match in self.gameday_matches],  
            'four_matches_list': [match.to_dict() for match in self.four_matches_list]
                }


    @classmethod
    def from_dict(cls, data):
        gameday_players = [GameDayPlayer.from_dict(player_data) for player_data in data['gameday_players']]
        gameday_matches = [Match.from_dict(match_data) for match_data in data['gameday_matches']]
        four_matches_list = [Match.from_dict(match_data) for match_data in data['four_matches_list']]
        obj = cls(substitute_player=data['substitute_player'])
        obj.game_day_date = data['game_day_date']
        obj.gameday_players = gameday_players
        obj.gameday_matches = gameday_matches
        obj.four_matches_list = four_matches_list
        return obj
    

def deserialize_gameday_obj(session):
    gameday_data = session.get('gameday_object')
    gameday = GameDay.from_dict(gameday_data)
    return gameday
    
def serialize_gameday_obj(session, gameday_obj):
    session['gameday_object'] = gameday_obj.to_dict()




if __name__=='__main__':
    with app.app_context():
        gameday = GameDay(substitute_player='john')
        gameday_dict = gameday.to_dict()
        gameday_obj_restored = GameDay.from_dict(gameday_dict)

        gameday.display_four_matches_list_details()
    
        played_match = Match(
        match_start_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        player_1_login_name='jane',
        player_2_login_name='bill',
        match_result={(1,1),(2,1),(1,4),(1,6),(1,6)})

        gameday.update_match_status(played_match=played_match, match_status = 'played')

        print('Match has been updated')

        gameday.display_four_matches_list_details()

        # for player in gameday.gameday_players:
        #     print(f'Player: {player.player_login_name}. Player status: {player.player_status}')

        # gameday.update_gameday_player(player_1_login_name='mike',player_2_login_name='jane', status = 'ACTIVE', last_played=datetime.now())
        
        # print('Players have been updated')

        # for player in gameday.gameday_players:
        #     print(f'Player: {player.player_login_name}. Player status: {player.player_status}. Last played: {player.last_played}')







