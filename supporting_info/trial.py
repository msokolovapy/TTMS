import sys
import json
import zlib



gameday_obj = {'gameday_date': '2024-12-21', 'gameday_players_data': [], 'gameday_players': [{'player_login_name': 'james', 'player_rank': 1100.0, 'player_role': 'user', 'last_played': None, 'player_status': 'reserve', 'players_played_already': []}, {'player_login_name': 
'john', 'player_rank': 1508.76, 'player_role': 'admin', 'last_played': None, 'player_status': 'reserve', 'players_played_already': []}], 'gameday_matches': [{'match_id': None, 'match_start_date_time': None, 'player_1_login_name': 'john', 'player_2_login_name': 'james', 'match_result': None, 'status': 'active', 'html_display_status': True}]}

print(sys.getsizeof(str(gameday_obj)))
json_dict = json.dumps(gameday_obj)
compressed_dict = zlib.compress(json_dict.encode('utf-8'))
print(sys.getsizeof(compressed_dict))

