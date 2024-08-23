from datetime import date

class Player:
    def __init__(self, player_login_name, player_phone_number, player_rank):
        self.player_login_name = player_login_name
        self.player_phone_number = player_phone_number
        self.player_rank = player_rank


class Match:
    def __init__(self, player_1_login_name,player_2_login_name, points_per_win): 
        self.player_1_login_name = player_1_login_name
        self.player_2_login_name = player_2_login_name
        points_per_win = points_per_win
        self.match_date = date.today()
        self.match_result = []
        self.winner = ''
        self.loser = ''
        self.total_points_winner = 0
        self.total_points_loser = 0
        
        
class RankingSystem:
    def __init__(self):
        self.player_lst = []
        self.matches_lst = []
        self.points_per_win = int(input('Enter how many points the player will gain per match won: '))
        self.current_max_total_points = 0

    def add_player(self, player_login_name, player_phone_number = '0411128965', player_rank = 0):
        new_player = Player(player_login_name, player_phone_number, player_rank)
        self.player_lst.append(new_player)
        return
    
    def add_match(self,player_1_login_name,player_2_login_name):
        new_match = Match(player_1_login_name,player_2_login_name, self.points_per_win)
        self.matches_lst.append(new_match)
        return
    
    def find_player(self, player_login_name):
        for player in self.player_lst:
            if player.player_login_name == player_login_name:
                return player
        return None
    
    def find_match(self,player_1_login_name,player_2_login_name):
        for match in self.matches_lst:
            if match.player_1_login_name == player_1_login_name and match.player_2_login_name == player_2_login_name:
                return match
        return None
    
    def save_match_results(self,match):
        number_games_played = int(input("Enter number of games played today: "))
        for i in range(number_games_played):
            game = []
            score_1 = float(input(f"Enter {match.player_1_login_name}'s score for match # {i+1}: "))
            score_2 = float(input(f"Enter {match.player_2_login_name}'s score for match # {i+1}: "))
            game.append(score_1)
            game.append(score_2)
            match.match_result.append(game)
        return
    
    def calculate_points(self,match):
            if match:
                games_won_by_player_1 = sum(1 for score in match.match_result if score[0] > score[1])
                games_won_by_player_2 = len(match.match_result) - games_won_by_player_1
                if games_won_by_player_1 > games_won_by_player_2:
                    match.winner = match.player_1_login_name
                    match.loser = match.player_2_login_name
                    average_margin = sum([score[0] - score[1] for score in match.match_result if score[0] > score[1]]) / games_won_by_player_1
                    match.total_points_winner = games_won_by_player_1 * self.points_per_win * average_margin 
                else:
                    match.winner = match.player_2_login_name
                    match.loser = match.player_1_login_name
                    average_margin = sum([score[1] - score[0] for score in match.match_result if score[1] > score[0]]) / games_won_by_player_2
                    match.total_points_winner = games_won_by_player_2 * self.points_per_win * average_margin 
   
    def save_max_points(self,match):
        if match.total_points_winner > self.current_max_total_points:
            self.current_max_total_points = match.total_points_winner
        else:
            pass
        return
    
    def update_ranking(self,match):
        total_players = len(self.player_lst)
        for player in self.player_lst:
            if player.player_login_name == match.winner:
                new_rank = total_players - (total_players * (match.total_points_winner / self.current_max_total_points))
                player.player_rank = max(1, new_rank)  # Ensure rank is not zero
            elif player.player_login_name == match.loser:
                player.player_rank = total_players
            else:
                player.player_rank = player.player_rank  # Keep the existing rank
            return


    def update_match_results(self,player_1_login_name,player_2_login_name):
        match = self.find_match(player_1_login_name,player_2_login_name)
        self.save_match_results(match)
        self.calculate_points(match)
        self.save_max_points(match)
        self.update_ranking(match)
        return


TTMS = RankingSystem()
TTMS_player_lst = ['mike','john','jeremy','maria', 'joel','sarah']
for i in range(len(TTMS_player_lst)):
    TTMS.add_player(TTMS_player_lst[i])
TTMS.add_match('mike','john')
TTMS.add_match('jeremy','maria')
TTMS.add_match('joel','sarah')
TTMS.update_match_results('mike','john')
TTMS.update_match_results('jeremy','maria')
TTMS.update_match_results('joel','sarah')
for match in TTMS.matches_lst:
    print(match.__dict__)
for player in TTMS.player_lst:
    print(player.__dict__)




