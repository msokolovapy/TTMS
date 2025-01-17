# from app import app, db
# from gameday import GameDay
# from datetime import datetime, timedelta


# def add_last_played_dates(serialized_players_list):
#     init_date = datetime.strptime('2024-12-01', "%Y-%m-%d")
#     for player_data in serialised_players_list:
#         for key,value in player_data.items():
#             if key == 'last_played':
#                 player_data[key] = init_date
#                 init_date += timedelta(days=1)
#     return serialised_players_list


# def create_drop_down_list(sorted_serialised_players_list):
#     simple_player_data_list = [{'original' : player_dict['player_login_name'],
#                                 'formatted' : f'{player_dict['player_login_name']} ({player_dict['player_rank']})'} 
#                                 for player_dict in sorted_serialised_players_list]
#     return tuple(simple_player_data_list)
    


# if __name__ =='__main__':
#     with app.app_context():
#         gameday_obj = GameDay()
#         gameday_players = gameday_obj.get_gameday_players()
#         serialised_players_list = [player.to_dict() for player in gameday_players]
#         serialised_players_list = add_last_played_dates(serialised_players_list)
#         for players_data in serialised_players_list:
#             if players_data['player_login_name'] == 'bill':
#                 players_data['last_played'] = None
#         sorted_serialised_players_list = sorted(serialised_players_list, key = 
#                                                 lambda x: x['last_played'] if x['last_played'] is not None 
#                                                 else datetime(1,1,1))
#         print(create_drop_down_list(sorted_serialised_players_list))


from datetime import datetime     
a = datetime.strptime('2024-12-04 00:00:00','%Y-%m-%d %H:%M:%S')
print(a)
print(type(a))