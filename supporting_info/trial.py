#trial.py
import ast

def convert_match_result_to_tuple(match):
    match = ast.literal_eval(match)
    return tuple([tuple(map(int, score_duo)) for score_duo in match])

match = "(('1', '1'), ('1', '1'), ('1', '1'), ('1', '1'), ('1', '1'))"

match = convert_match_result_to_tuple(match)
print(match)

