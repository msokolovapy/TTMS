from flask import flash, session
from sqlalchemy import cast, Float
from datetime import datetime
from ttms import db,bcrypt
from ttms.models_booking import Booking


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
        player.player_status = data.get('player_status', 'reserve') 
        player.players_played_already = data.get('players_played_already', []) 
    
        return player

def find_user_in_database_by(player_email):
    return User.query.filter_by(player_email_address = player_email).first()

def create_user_from(user_info):
    user = User(player_login_name=user_info['user_name'],
            player_email_address=user_info['user_email'],
            player_phone_number=user_info['user_phone_number'],
            player_password=bcrypt.generate_password_hash(user_info['user_password']).decode('utf-8'),
            player_role='user',
            player_rank=1500
        )
    return user

def user_is(role):
   if session.get('user_role') == role:
       return True
   return False

def user_is_logged_in():
   if 'user_id' in session:
       return True
   return False

def login_checks_pass():
   if user_is_logged_in() and user_is('admin'):
       return True
   return False  


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
            print('Gameday players list empty. Impossible to update')

    def to_dict(self):
        return {
            'gameday_date': self.gameday_date,
            'gameday_players': [player.to_dict() for player in self.gameday_players]}

    @classmethod
    def from_dict(cls, data):
        gameday_players = [GameDayPlayer.from_dict(player_data) for player_data in data['gameday_players']]
        obj = cls()
        obj.gameday_date = data['gameday_date']
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
