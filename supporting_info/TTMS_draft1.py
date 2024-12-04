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
        self.points_per_win = int(input('Enter how many points the player will gain per game won: '))
        self.current_max_total_points = 0
        self.points_per_game = int(input('Enter maximum number of points a player may score per game: '))

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
    
    def save_match_results(self, match):
    # Validate number of games played (must be an odd number)
        while True:
            try:
                number_games_played = int(input(f'How many games have {match.player_1_login_name} and {match.player_2_login_name} played today (must be an odd number): '))
                if number_games_played % 2 == 0:
                    print("The number of games must be an odd number. Please try again.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter an integer.")
        # Loop through the number of games and validate scores
        for i in range(number_games_played):
            game = []
            while True:
                try:
                    score_1 = float(input(f"Enter {match.player_1_login_name}'s score for game # {i+1} (between 0 and {self.points_per_game}): "))
                    if 0 <= score_1 <= self.points_per_game:
                        break
                    else:
                        print(f"Score must be between 0 and {self.points_per_game}. Please try again.")
                except ValueError:
                    print(f"Invalid input. Please enter a number between 0 and {self.points_per_game}.")
            while True:
                try:
                    score_2 = float(input(f"Enter {match.player_2_login_name}'s score for game # {i+1} (between 0 and {self.points_per_game}): "))
                    if 0 <= score_2 <= self.points_per_game:
                        break
                    else:
                        print(f"Score must be between 0 and {self.points_per_game}. Please try again.")
                except ValueError:
                    print(f"Invalid input. Please enter a number between 0 and {self.points_per_game}.")
            game.append(score_1)
            game.append(score_2)
            match.match_result.append(game)
        return

    
    def calculate_points(self,match):
        if match:
            games_won_by_player_1 = sum(1 for score in match.match_result if score[0] > score[1])
            games_won_by_player_2 = len(match.match_result) - games_won_by_player_1       
            try:
                average_margin_player_1 = sum([score[0] - score[1] for score in match.match_result if score[0] > score[1]]) / games_won_by_player_1
            except ZeroDivisionError:
                average_margin_player_1 = sum([score[0] - score[1] for score in match.match_result if score[0] > score[1]])    
            try:    
                average_margin_player_2 = sum([score[1] - score[0] for score in match.match_result if score[1] > score[0]]) / games_won_by_player_2
            except ZeroDivisionError:
                average_margin_player_2 = sum([score[1] - score[0] for score in match.match_result if score[1] > score[0]])
                
            if games_won_by_player_1 > games_won_by_player_2:
                match.winner = match.player_1_login_name
                match.loser = match.player_2_login_name
                match.total_points_winner = (games_won_by_player_1 * self.points_per_win) + (games_won_by_player_1 * self.points_per_win * (average_margin_player_1/self.points_per_game))
                match.total_points_loser = (games_won_by_player_2 * self.points_per_win) + (games_won_by_player_2 * self.points_per_win * (average_margin_player_2/self.points_per_game))
            else:
                match.winner = match.player_2_login_name
                match.loser = match.player_1_login_name
                match.total_points_winner = (games_won_by_player_2 * self.points_per_win) + (games_won_by_player_2 * self.points_per_win * (average_margin_player_2/self.points_per_game))
                match.total_points_loser = (games_won_by_player_1 * self.points_per_win) + (games_won_by_player_1 * self.points_per_win * (average_margin_player_1/self.points_per_game))
            # print(f'total points winner for match between {match.winner} and {match.loser} = {match.total_points_winner}')
            # print(f'total points loser for match between {match.winner} and {match.loser} = {match.total_points_loser}')
            # print(f'games won by player 1: {games_won_by_player_1}')
            # print(f'games won by player 2: {games_won_by_player_2}')
            # print(f'average points margin for player 1: {average_margin_player_1}')
            # print(f'average points margin for player 2: {average_margin_player_2}')
        return
    
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
                player.player_rank = total_players - (total_players * (match.total_points_winner / self.current_max_total_points))
            elif player.player_login_name == match.loser:
                player.player_rank = total_players - (total_players * (match.total_points_loser / self.current_max_total_points))
            else:
                player.player_rank = player.player_rank  # Keep the existing rank
        return


    def update_match_results(self):
        for match in self.matches_lst:
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
TTMS.update_match_results()
for match in TTMS.matches_lst:
    print(match.__dict__)
for player in TTMS.player_lst:
    print(player.__dict__)




