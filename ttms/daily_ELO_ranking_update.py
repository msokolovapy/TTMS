# daily_ranking_update.py

"""IMPORTANT: schedule daily running of this module to ensure timely player ranking update"""

from ttms import app,db
from datetime import datetime
from ttms.models_match import retrieve_match_data
from ttms.models_user import User
import logging

logging.basicConfig(filename='daily_ranking_update_log.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')


def update_database_with_new_ranks(match):
    winner_name, loser_name = match.determine_match_winner()
    new_winner_rank, new_loser_rank = match.update_player_ranking()

    winner = User.query.filter_by(player_login_name=winner_name).first()
    loser = User.query.filter_by(player_login_name=loser_name).first()
    winner.player_rank = new_winner_rank
    loser.player_rank = new_loser_rank

    db.session.commit()


def daily_ranking_update(match_obj_list):
    if match_obj_list:
        for match_obj in match_obj_list:
            update_database_with_new_ranks(match_obj)
            logging.info(f"Updated player ranking for match between {match_obj.player_1_login_name} and {match_obj.player_2_login_name}.")
    else:
        logging.info("No match objects to update.")

def main():
    with app.app_context():
        try:
            today_date = datetime.now().strftime('%Y-%m-%d')
            match_obj_list = retrieve_match_data(today_date) 
            if match_obj_list:               
                daily_ranking_update(match_obj_list)
                logging.info("Daily player ranking update completed successfully.")
            else:
                logging.info(f"No matches found for {today_date}")
        except Exception as e:
            logging.error(f"Error occurred during player ranking update: {e}")



if __name__ == '__main__':
    main()



    