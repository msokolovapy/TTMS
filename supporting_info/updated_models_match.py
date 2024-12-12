#updated_models_match.py

from datetime import date
import ast

class RankingSystem():

    def __init__(self, max_total_points = None, points_per_win = None):
        self.max_total_points = max_total_points
        self.points_per_win = points_per_win

    def get_max_total_points(self):
        return self.max_total_points

    def set_max_total_points(self, value):
        self.max_total_points = value

    def get_points_per_win(self):
        return self.points_per_win

    def set_points_per_win(self, value):
        self.points_per_win = value


class Match:
    def __init__(self, player_1_login_name,player_2_login_name, match_result = None, rank_system_obj = None): 
        self.player_1_login_name = player_1_login_name
        self.player_2_login_name = player_2_login_name
        self.match_result = match_result
        self.rank_system_obj = rank_system_obj
        

    def convert_match_result_to_integer(self):
        if self.match_result:
            match_result = ast.literal_eval(self.match_result)
            return tuple([tuple(map(int, score_duo)) for score_duo in match_result])
        else:
            print("Match result doesn't exist. Impossible to convert to tuple")

    
    def calculate_points(self, match):
        match_result = self.convert_match_result_to_integer()

        #logic here for dealing with a tie

        games_won_by_player_1 = sum(1 for score_duo in match_result if score_duo[0] > score_duo[1])
        games_won_by_player_2 = len(match.match_result) - games_won_by_player_1       
        try:
            average_margin_player_1 = sum([score_duo[0] - score_duo[1] for score_duo in match_result if score_duo[0] > score_duo[1]]) / games_won_by_player_1
        except ZeroDivisionError:
            average_margin_player_1 = 0   
        try:    
            average_margin_player_2 = sum([score_duo[1] - score_duo[0] for score_duo in match_result if score_duo[1] > score_duo[0]]) / games_won_by_player_2
        except ZeroDivisionError:
            average_margin_player_2 = 0
                
            if games_won_by_player_1 > games_won_by_player_2:  
                match.winner = match.player_1_login_name
                match.loser = match.player_2_login_name
                match.total_points_winner = (games_won_by_player_1 * self.points_per_win) + (games_won_by_player_1 * self.points_per_win * (average_margin_player_1/self.points_per_game))
                match.total_points_loser = (games_won_by_player_2 * self.points_per_win) + (games_won_by_player_2 * self.points_per_win * (average_margin_player_2/self.points_per_game))
            elif games_won_by_player_1 < games_won_by_player_2:
                match.winner = match.player_2_login_name
                match.loser = match.player_1_login_name
                match.total_points_winner = (games_won_by_player_2 * self.points_per_win) + (games_won_by_player_2 * self.points_per_win * (average_margin_player_2/self.points_per_game))
                match.total_points_loser = (games_won_by_player_1 * self.points_per_win) + (games_won_by_player_1 * self.points_per_win * (average_margin_player_1/self.points_per_game))
            else:
                #include instructions on what to do when there is a tie
                pass
     
    
    def save_max_points(self):
        if self.total_points_winner > self.r:
            current_max_total_points = self.total_points_winner
        else:
            pass

    
    def update_ranking(self,match,current_max_total_points):
        total_players = len(self.player_lst)
        for player in self.player_lst:
            if player.player_login_name == match.winner:
                player.player_rank = total_players - (total_players * (self.total_points_winner / current_max_total_points))
            else:
                player.player_login_name == match.loser
                player.player_rank = total_players - (total_players * (self.total_points_loser / current_max_total_points))


