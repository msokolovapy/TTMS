#run.py
from ttms import app

if __name__ == '__main__':
    app.run(debug=True)
# with app.app_context():
#     from ttms.gameday import Players, Matches
#     from ttms.models_match import Match
#     players = Players()
#     matches = Matches(players)
#     for match in matches.gameday_matches:
#         print(match.player_1_login_name, match.player_2_login_name)
#     print([(match.player_1_login_name,match.html_display_status) for match in matches.to_display()])
#     match_to_update = Match('jane','meredith')
#     matches.update_match(match_to_update,'Jack','Jill','played', False)
#     for match in matches.gameday_matches:
#         print(match.player_1_login_name, match.player_2_login_name, match.status)

#     players.update_gameday_player('jane', 'meredith',status = 'CHECK', last_played = 'CHECK')
#     for player in players.gameday_players:
#         print(player.player_login_name, player.last_played, player.player_status, player.players_played_already)

#     sorted_serialised_players_list = players.sort_gameday_players()
#     print(sorted_serialised_players_list)



