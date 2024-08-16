class Player:
    def __init__(self, player_login_name, player_phone_number, player_rank=None, latest_score = 0,number_wins = 0, number_losses = 0, number_matches_played = 0):
        self.player_login_name = player_login_name
        self.player_phone_number = player_phone_number
        self.player_rank = player_rank
        self.latest_score = latest_score
        self.number_wins = number_wins
        self.number_losses = number_losses
        self.number_matches_played = number_matches_played


class Match:
    def __init__(self, player_1_login_name,player_2_login_name):
        self.player_1_login_name = player_1_login_name
        self.player_2_login_name = player_2_login_name
        self.score_1 = int(input(f"Enter {player_1_login_name}'s score: "))
        self.score_2 = int(input(f"Enter {player_2_login_name}'s score: "))
        

class RankingSystem:
    def __init__(self):
        self.player_lst = []

    def add_player(self, player_login_name, player_phone_number, player_rank=None, number_wins=0, number_losses=0, number_matches_played=0):
        new_player = Player(player_login_name, player_phone_number, player_rank, number_wins, number_losses, number_matches_played)
        self.player_lst.append(new_player)
        return
    
    def find_player(self, player_login_name):
        for player in self.player_lst:
            if player.player_login_name == player_login_name:
                return player
        return None

    def update_match_results(self, match):
        player_1 = self.find_player(match.player_1_login_name)
        player_2 = self.find_player(match.player_2_login_name)
        
        if player_1 is None or player_2 is None:
            raise ValueError("One or both players not found")

        player_1.number_matches_played += 1
        player_2.number_matches_played += 1

        player_1.latest_score = match.score_1
        player_2.latest_score = match.score_2

        if match.score_1 > match.score_2:
            player_1.number_wins += 1
            player_2.number_losses += 1
        elif match.score_1 < match.score_2:
            player_2.number_wins += 1
            player_1.number_losses += 1
        else:
            # Handle tie situation if needed
            pass
        return

TTMS = RankingSystem()
TTMS.add_player('mike','0415263565')
TTMS.add_player('john','0412347898')
match_1 = Match('mike','john')
TTMS.update_match_results(match_1)
for player in TTMS.player_lst:
    print(player.__dict__)



