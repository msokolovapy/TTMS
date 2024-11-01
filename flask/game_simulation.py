#Here is the final table after running the simulation for 5 games using the new rankings as initial rankings:

import random

# Define Player class
class Player:
    def __init__(self, player_id, initial_ranking):
        self.player_id = player_id
        self.initial_ranking = initial_ranking
        self.wins = 0
        self.losses = 0
        self.points_from_wins = 0
        self.average_margin = 0
        self.total_points = 0
        self.new_ranking = 0

    def update_match_result(self, win, margin):
        if win:
            self.wins += 1
            self.points_from_wins += 1
            self.average_margin += margin
        else:
            self.losses += 1

    def calculate_final_points(self):
        if self.wins > 0:
            self.average_margin /= self.wins
        self.total_points = self.points_from_wins * self.average_margin

    def normalize_ranking(self, max_points, num_players=12):
        self.new_ranking = round(12 - 12 * (self.total_points / max_points),2)
        if self.new_ranking <= 0:
            self.new_ranking = 1

# Define Match class
class Match:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.simulate_match()

    def simulate_match(self):
        # Simulate the match outcome based on initial rankings
        p1_advantage = self.player1.initial_ranking / (self.player1.initial_ranking + self.player2.initial_ranking)
        outcome = random.random()
        margin = random.uniform(0.1, 1.0)

        if outcome < p1_advantage:
            self.player1.update_match_result(True, margin)
            self.player2.update_match_result(False, margin)
        else:
            self.player1.update_match_result(False, margin)
            self.player2.update_match_result(True, margin)

# Define RankingSystem class
class RankingSystem:
    def __init__(self, players):
        self.players = players

    def simulate_round(self, num_matches):
        # Pair players randomly and simulate matches
        random.shuffle(self.players)
        for i in range(0, len(self.players), 2):
            Match(self.players[i], self.players[i+1])

    def recalculate_rankings(self):
        max_points = 0
        for player in self.players:
            player.calculate_final_points()
            if player.total_points > max_points:
                max_points = player.total_points

        # Normalize rankings
        for player in self.players:
            player.normalize_ranking(max_points)

    def display_rankings(self):
        return [
            {
                "Player": player.player_id,
                "Initial Ranking": player.initial_ranking,
                "Wins": player.wins,
                "Losses": player.losses,
                "Points from Wins": player.points_from_wins,
                "Average Margin": round(player.average_margin, 2),
                "Total Points": round(player.total_points, 2),
                "New Ranking": player.new_ranking
            }
            for player in self.players
        ]

# Initial data
initial_rankings = [6, 6, 9, 9, 6, 6, 3, 3, 3, 3, 9, 9]
players = [Player(f'P{i+1}', rank) for i, rank in enumerate(initial_rankings)]

# Create Ranking System
ranking_system = RankingSystem(players)

# Simulate 5 rounds of matches
for _ in range(5):
    ranking_system.simulate_round(num_matches=6)  # 6 matches with 12 players

# Recalculate Rankings
ranking_system.recalculate_rankings()

# Display final rankings
final_rankings = ranking_system.display_rankings()
for record in final_rankings:
    player = record['Player']
    initial_ranking = record['Initial Ranking']
    new_ranking = record['New Ranking']
    
    # Format and print the output
    print(f"{player}|{initial_ranking}|{new_ranking}")