# daily_ranking_update.py

from datetime import datetime
from extensions import db
from models_match import Match
from sqlalchemy import func
import logging

logging.basicConfig(filename='daily_ranking_update.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

def retrieve_match_data(match_date):
    # today_date = datetime.now().strftime('%Y-%m-%d')
    match_data_query = db.session.query(
        Match.player_1_login_name,
        Match.player_2_login_name,
        Match.match_result
    ).filter(func.date(Match.match_start_date_time) == match_date).all()
    
    logging.info(f"Retrieved match data for {match_date}")
    return match_data_query

def create_match_obj_list(match_date):
    match_data_query_result = retrieve_match_data(match_date)
    if match_data_query_result:
        match_obj_list = [
            Match(player_1_login_name=player_1_login_name, player_2_login_name=player_2_login_name, match_result=match_result)
            for (player_1_login_name, player_2_login_name, match_result) in match_data_query_result
        ]
        logging.info(f"Created match object list with {len(match_obj_list)} matches.")
    else:
        match_obj_list = []  # Empty list if no matches found
        logging.info("No games were played today. No match objects created.")
    return match_obj_list

def daily_ranking_update(match_obj_list):
    if match_obj_list:
        for match_obj in match_obj_list:
            match_obj.update_ranking()
            logging.info(f"Updated player ranking for match between {match_obj.player_1_login_name} and {match_obj.player_2_login_name}.")
    else:
        logging.info("No match objects to update.")



if __name__ == '__main__':
    try:
        match_obj_list = create_match_obj_list()
        daily_ranking_update(match_obj_list)
        logging.info("Daily player ranking update completed successfully.")
    except Exception as e:
        logging.error(f"Error occurred during player ranking update: {e}")


    