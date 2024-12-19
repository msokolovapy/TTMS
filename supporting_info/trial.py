def calculate_elo(winner_rating, loser_rating, k_factor=32):
    """
    Calculate updated Elo ratings for winner and loser.
    
    Parameters:
    - winner_rating (float): Current Elo rating of the winner.
    - loser_rating (float): Current Elo rating of the loser.
    - k_factor (int): K-factor that controls the adjustment size. Default is 32.
    
    Returns:
    - tuple: Updated ratings for the winner and loser (winner_new_rating, loser_new_rating).
    """
    
    # Calculate the expected score for both players
    expected_winner_score = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser_score = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    
    # Since the winner actually won, the score is 1 for the winner and 0 for the loser
    actual_winner_score = 1
    actual_loser_score = 0
    
    # Update the winner's and loser's ratings using the Elo formula
    winner_new_rating = winner_rating + k_factor * (actual_winner_score - expected_winner_score)
    loser_new_rating = loser_rating + k_factor * (actual_loser_score - expected_loser_score)
    
    return round(winner_new_rating, 2), round(loser_new_rating, 2)



