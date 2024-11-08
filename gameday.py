#gameday.py
from app import app
from sqlalchemy import cast, Float
from extensions import db
from models_booking import Booking
from models_user import User, GameDayPlayer
from models_match import Match
from datetime import datetime
import random




class GameDay():
    def __init__(self):
        self.game_day_date = self.obtain_game_day_date()
        self.game_day_players_data = self.obtain_game_day_players_data()
        self.gameday_players = self.create_gameday_players_lst()
        self.gameday_matches = None

    def obtain_game_day_date(self):
        #find the earliest booking date >= current date
        game_day_date = db.session.query(Booking.required_booking_date)\
            .filter(Booking.required_booking_date >= datetime.today())\
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
        return [GameDayPlayer(player_data) for player_data in self.game_day_players_data]

    def create_gameday_match_lst(self,user_name):
        matched_duos = self.match_players(user_name)
        match_lst = []
        for matched_duo in matched_duos:
            player_1_login_name, player_2_login_name = matched_duo
            match = Match(player_1_login_name=player_1_login_name, player_2_login_name=player_2_login_name)
            match.status = 'inactive'
            match_lst.append(match)
        return match_lst

        
    def match_players(self,user_name):
        game_day_players_data = self.game_day_players_data.copy()
        matched_players = []
        random.shuffle(game_day_players_data)
        if len(game_day_players_data) % 2 != 0: #odd number of players, one players randomly popped off list and matched with admin
            random_index = random.randint(0, len(game_day_players_data) - 1)
            player_login_name = game_day_players_data.pop(random_index)[0]
            matched_players.append([user_name,player_login_name])
        while len(game_day_players_data) > 1:
            player_login_name, player_rank = game_day_players_data.pop()  # Pop a player from the end
            game_day_players_data.sort(key=lambda x: abs(x[1] - player_rank))  # Sort based on rank difference
            closest_match = game_day_players_data.pop(0)  # Pop the closest match
            matched_players.append((closest_match[0], player_login_name))
        return matched_players


    def load_matches(self,user_name):
        self.gameday_matches = self.create_gameday_match_lst(user_name)
        random.shuffle(self.gameday_matches) #provides randomly shuffled gameday.gameday_matches list
        four_matches_list = self.gameday_matches[:4] # provides first four match objects
        return four_matches_list

if __name__=='__main__':
    with app.app_context():
        gameday = GameDay()
        gamedate = gameday.obtain_game_day_date()
        gameday_players_data = gameday.obtain_game_day_players_data()
        gameday_players_list = gameday.create_gameday_players_lst()
        print(gamedate)
        print(gameday_players_data)
        for gameday_player in gameday_players_list:
            print(gameday_player.player_login_name)
        gameday.load_matches('john')





