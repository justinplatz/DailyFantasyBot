import random
import pandas as pd
from config import POPSIZE, MAXEXPOSURE, MAXCOST

def splice_and_combine_parents(parent_one, parent_two, players_df):
    combined = pd.concat([parent_one, parent_two])

    qb = combined.loc[combined['lineup_position'] == "QB"].sample(1)
    rb1 = combined.loc[combined['lineup_position'] == "RB1"].sample(1)
    rb2 = combined.loc[combined['lineup_position'] == "RB2"].sample(1)
    wr1 = combined.loc[combined['lineup_position'] == "WR1"].sample(1)
    wr2 = combined.loc[combined['lineup_position'] == "WR2"].sample(1)
    wr3 = combined.loc[combined['lineup_position'] == "WR3"].sample(1)
    te = combined.loc[combined['lineup_position'] == "TE"].sample(1)
    dst = combined.loc[combined['lineup_position'] == "DST"].sample(1)
    flex = combined.loc[combined['lineup_position'] == "FLEX"].sample(1)

    lineup = pd.DataFrame()
    lineup = lineup.append([qb, rb1, rb2, wr1, wr2, wr3, te, flex, dst])
    lineup = remove_duplicates_from_lineup(lineup, players_df)

    cost = get_cost_from_lineup(lineup)
    if (cost > MAXCOST):
        lineup = parent_one

    score = get_score_from_lineup(lineup)
    cost = get_cost_from_lineup(lineup)
    random_lineup_id = random.getrandbits(32)

    lineup = lineup.assign(lineup_cost=cost)
    lineup = lineup.assign(lineup_score=score)
    lineup = lineup.assign(lineup_id=random_lineup_id)

    return lineup

def generate_random_lineups(players_df):
    population = pd.DataFrame()
    child = generate_random_child(players_df)
    population = pd.concat([population,child])

    while len(population["lineup_id"].unique()) < POPSIZE:
        child = generate_random_child(players_df)

        temp = population
        temp = pd.concat([temp,child])

        if enforce_max_exposure(temp):
            population = pd.concat([population, child])

    return population

def generate_random_child(players_df):
    lineup = generate_random_lineup(players_df)
    lineup = remove_duplicates_from_lineup(lineup, players_df)

    cost = get_cost_from_lineup(lineup)
    if (cost > MAXCOST):
        return generate_random_child(players_df)

    score = get_score_from_lineup(lineup)
    random_lineup_id = random.getrandbits(32)

    lineup = lineup.assign(lineup_cost=cost)
    lineup = lineup.assign(lineup_score=score)
    lineup = lineup.assign(lineup_id=random_lineup_id)

    return lineup

def generate_random_lineup(players_df):
    try:
        bugdet = MAXCOST

        qb = players_df.loc[(players_df["position"] == "QB") & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= qb["salary"].values[0]

        rb1 = players_df.loc[(players_df["position"] == "RB") & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= rb1["salary"].values[0]

        rb2 = players_df.loc[(players_df["position"] == "RB") & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= rb2["salary"].values[0]

        wr1 = players_df.loc[(players_df["position"] == "WR") & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= wr1["salary"].values[0]
        wr2 = players_df.loc[(players_df["position"] == "WR") & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= wr2["salary"].values[0]

        flex = players_df.loc[(players_df['position'].isin(["RB","WR"])) & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= flex["salary"].values[0]

        wr3 = players_df.loc[(players_df["position"] == "WR") & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= wr3["salary"].values[0]

        te = players_df.loc[(players_df["position"] == "TE") & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= te["salary"].values[0]

        dst = players_df.loc[(players_df["position"] == "DST") & (players_df["salary"] <= bugdet)].sample(n=1)
        bugdet -= dst["salary"].values[0]

        qb["lineup_position"] = "QB"
        rb1["lineup_position"] = "RB1"
        rb2["lineup_position"] = "RB2"
        wr1["lineup_position"] = "WR1"
        wr2["lineup_position"] = "WR2"
        wr3["lineup_position"] = "WR3"
        te["lineup_position"] = "TE"
        dst["lineup_position"] = "DST"
        flex["lineup_position"] = "FLEX"

        lineup_df = pd.DataFrame()
        lineup_df = lineup_df.append([qb, rb1, rb2, wr1, wr2, wr3, te, flex, dst])

        return lineup_df
    except:
        return generate_random_lineup(players_df)

def get_score_from_lineup(lineup):
    score = lineup["score"].sum()
    return score

def get_cost_from_lineup(lineup):
    cost = lineup["salary"].sum()
    return cost

def remove_duplicates_from_lineup(lineup, players_df):
    lineup = lineup.drop_duplicates(subset='ID', keep='first')
    # check for rb1
    if not (lineup['lineup_position'] == 'RB1').any():
        rb1 = players_df.loc[(players_df["position"] == "RB")].sample(n=1)
        rb1["lineup_position"] = "RB1"
        lineup = lineup.append(rb1)
        return remove_duplicates_from_lineup(lineup, players_df)

    #check for rb2
    if not (lineup['lineup_position'] == 'RB2').any():
        rb2 = players_df.loc[(players_df["position"] == "RB")].sample(n=1)
        rb2["lineup_position"] = "RB2"
        lineup = lineup.append(rb2)
        return remove_duplicates_from_lineup(lineup, players_df)

    #check for wr1
    if not (lineup['lineup_position'] == 'WR1').any():
        wr1 = players_df.loc[(players_df["position"] == "WR")].sample(n=1)
        wr1["lineup_position"] = "WR1"
        lineup = lineup.append(wr1)
        return remove_duplicates_from_lineup(lineup, players_df)

    # check for wr2
    if not (lineup['lineup_position'] == 'WR2').any():
        wr2 = players_df.loc[(players_df["position"] == "WR")].sample(n=1)
        wr2["lineup_position"] = "WR2"
        lineup = lineup.append(wr2)

        return remove_duplicates_from_lineup(lineup, players_df)

    # check for wr3
    if not (lineup['lineup_position'] == 'WR3').any():
        wr3 = players_df.loc[(players_df["position"] == "WR")].sample(n=1)
        wr3["lineup_position"] = "WR3"
        lineup = lineup.append(wr3)
        return remove_duplicates_from_lineup(lineup, players_df)

    # check for te
    if not (lineup['lineup_position'] == 'TE').any():
        te = players_df.loc[(players_df["position"] == "TE")].sample(n=1)
        te["lineup_position"] = "TE"
        lineup = lineup.append(te)
        return remove_duplicates_from_lineup(lineup, players_df)

    # check for flex
    if not (lineup['lineup_position'] == 'FLEX').any():
        flex = players_df.loc[(players_df['position'].isin(["RB", "WR"]))].sample(n=1)
        flex["lineup_position"] = "FLEX"
        lineup = lineup.append(flex)
        return remove_duplicates_from_lineup(lineup, players_df)

    return lineup

def enforce_max_exposure(population):

    counts = (population['ID'].value_counts() / POPSIZE) < MAXEXPOSURE
    for is_under_max_exposure in counts:
        if not is_under_max_exposure:
            return False

    return True

# def select_random_lineup_from_population(population):
#     lineup_id = population.sample(1)["lineup_id"].values[0]
#     lineup = population.loc[population['lineup_id'] == lineup_id]
#     return lineup

def select_random_lineup_from_population(population, alpha_decay):
    population = population.sort_values(by=['lineup_score'], ascending=False)
    lineup_id = population.tail(alpha_decay).sample(1)["lineup_id"].values[0]
    lineup = population.loc[population['lineup_id'] == lineup_id]
    return lineup
