import random
from copy import deepcopy

from lineup_utils import remove_duplicates_from_lineup, get_cost_from_lineup, get_score_from_lineup, generate_random_child
from config import MAXCOST

def update_lineup_score_and_cost(child_lineup):
    score = get_score_from_lineup(child_lineup)
    cost = get_cost_from_lineup(child_lineup)
    child_lineup = child_lineup.assign(lineup_cost=cost)
    child_lineup = child_lineup.assign(lineup_score=score)
    return child_lineup

def swap_for_higher_pos_rank(lineup, players_df):
    try:
        drop_player = lineup.sample(n=1)

        position = drop_player["position"].values[0]
        posrank = drop_player["positionECR"].values[0]
        lineup_position = drop_player["lineup_position"].values[0]
        lineup_cost = drop_player["lineup_cost"].values[0]
        salary = drop_player["salary"].values[0]

        budget = (MAXCOST - lineup_cost) + salary

        new_player = players_df.loc[
            (players_df["position"] == position) &
            (players_df["positionECR"] >= posrank) &
            (players_df["salary"] <= budget)
        ].head(5).sample(n=1)

        new_player["lineup_position"] = lineup_position

        lineup = lineup.drop(drop_player.index[0])
        lineup = lineup.append([new_player])

        return lineup
    except:
        return lineup

def swap_for_lower_pos_rank(lineup, players_df):
    try:
        drop_player = lineup.sample(n=1)

        position = drop_player["position"].values[0]
        posrank = drop_player["positionECR"].values[0]
        lineup_position = drop_player["lineup_position"].values[0]
        lineup_cost = drop_player["lineup_cost"].values[0]
        salary = drop_player["salary"].values[0]

        budget = (MAXCOST - lineup_cost) + salary

        new_player = players_df.loc[
            (players_df["position"] == position) &
            (players_df["positionECR"] <= posrank) &
            (players_df["salary"] <= budget)
            ].head(5).sample(n=1)

        new_player["lineup_position"] = lineup_position

        lineup = lineup.drop(drop_player.index[0])
        lineup = lineup.append([new_player])

        return lineup
    except:
        return lineup

def swap_random_player(lineup, players_df):

    drop_player = lineup.sample(n=1)
    position = drop_player["position"].values[0]
    lineup_position = drop_player["lineup_position"].values[0]
    salary = drop_player["salary"].values[0]
    lineup_cost = drop_player["lineup_cost"].values[0]

    budget = (MAXCOST - lineup_cost) + salary

    new_player = players_df.loc[
        (players_df["position"] == position) &
        (players_df["salary"] <= budget)
    ].head(5).sample(n=1)

    new_player["lineup_position"] = lineup_position

    lineup = lineup.drop(drop_player.index[0])
    lineup = lineup.append([new_player])

    return lineup

def swap_for_higher_tier(lineup, players_df):
    try:
        drop_player = lineup.sample(n=1)

        position = drop_player["position"].values[0]
        posrank = drop_player["positionECR"].values[0]
        lineup_position = drop_player["lineup_position"].values[0]
        lineup_cost = drop_player["lineup_cost"].values[0]
        salary = drop_player["salary"].values[0]

        budget = (MAXCOST - lineup_cost) + salary

        new_player = players_df.loc[
            (players_df["position"] == position) &
            (players_df["tier"] >= posrank) &
            (players_df["salary"] <= budget)
            ].head(5).sample(n=1)

        new_player["lineup_position"] = lineup_position

        lineup = lineup.drop(drop_player.index[0])
        lineup = lineup.append([new_player])

        return lineup
    except:
        return lineup

def swap_for_lower_tier(lineup, players_df):
    try:
        drop_player = lineup.sample(n=1)

        position = drop_player["position"].values[0]
        posrank = drop_player["positionECR"].values[0]
        lineup_position = drop_player["lineup_position"].values[0]
        lineup_cost = drop_player["lineup_cost"].values[0]
        salary = drop_player["salary"].values[0]

        budget = (MAXCOST - lineup_cost) + salary

        new_player = players_df.loc[
            (players_df["position"] == position) &
            (players_df["tier"] <= posrank) &
            (players_df["salary"] <= budget)
            ].head(5).sample(n=1)

        new_player["lineup_position"] = lineup_position

        lineup = lineup.drop(drop_player.index[0])
        lineup = lineup.append([new_player])

        return lineup
    except:
        return lineup

def swap_out_lowest_scorer(lineup, players_df):
    try:
        drop_player = lineup[lineup["score"] == lineup["score"].min()]
        score = drop_player["score"].values[0]
        position = drop_player["position"].values[0]
        salary = drop_player["salary"].values[0]
        lineup_position = drop_player["lineup_position"].values[0]
        lineup_cost = drop_player["lineup_cost"].values[0]

        budget = (MAXCOST - lineup_cost) + salary

        new_player = players_df.loc[
            (players_df["position"] == position) &
            (players_df["score"] >= score) &
            (players_df["salary"] <= budget)
        ].head(2).sample(n=1)

        new_player["lineup_position"] = lineup_position

        lineup = lineup.drop(drop_player.index[0])
        lineup = lineup.append([new_player])

        return lineup
    except:
        return lineup


def apply_mutations(child_lineup, players_df, alpha_decay):

    random_val = random.randint(1, 100)
    if (random_val <= alpha_decay):
        child_lineup = swap_random_player(child_lineup, players_df)
        child_lineup = update_lineup_score_and_cost(child_lineup)

    random_val = random.randint(1, 100)
    if (random_val <= alpha_decay):
        child_lineup = swap_for_lower_pos_rank(child_lineup, players_df)
        child_lineup = update_lineup_score_and_cost(child_lineup)

    random_val = random.randint(1, 100)
    if (random_val <= alpha_decay):
        child_lineup = swap_for_lower_tier(child_lineup, players_df)
        child_lineup = update_lineup_score_and_cost(child_lineup)

    random_val = random.randint(1, 100)
    if (random_val <= alpha_decay+50):
        child_lineup = swap_for_higher_pos_rank(child_lineup, players_df)
        child_lineup = update_lineup_score_and_cost(child_lineup)

    random_val = random.randint(1, 100)
    if (random_val <= alpha_decay+50):
        child_lineup = swap_for_higher_tier(child_lineup, players_df)
        child_lineup = update_lineup_score_and_cost(child_lineup)

    random_val = random.randint(1, 100)
    if (random_val <= alpha_decay+75):
        child_lineup = swap_out_lowest_scorer(child_lineup, players_df)
        child_lineup = update_lineup_score_and_cost(child_lineup)

    child_lineup = remove_duplicates_from_lineup(child_lineup, players_df)
    child_lineup = update_lineup_score_and_cost(child_lineup)

    cost = child_lineup.head(n=1)["lineup_cost"].values[0]

    if (cost > MAXCOST):
        return generate_random_child(players_df)
    else:
        return child_lineup