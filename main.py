import random
import math
import pandas as pd
from copy import deepcopy

from web import scrape_dk_ids_to_df
from lineup_utils import \
    splice_and_combine_parents, \
    generate_random_lineups, \
    select_random_lineup_from_population, \
    generate_random_child, \
    enforce_max_exposure,\
    get_cost_from_lineup, \
    get_score_from_lineup

from main_utils import \
    write_population_to_csv, \
    write_players_to_csv, \
    merge_dk_ids_and_ffa_stats

from mutations import apply_mutations

from config import MAXCOST, MAXGEN, POPSIZE

def main():

    players_df = scrape_dk_ids_to_df()
    players_df = merge_dk_ids_and_ffa_stats(players_df)
    write_players_to_csv(players_df)

    population = generate_random_lineups(players_df)

    population = population.sort_values(by=['lineup_score', 'lineup_id'], ascending=False)

    high_score = population.head(1)["lineup_score"].values[0]
    low_score = population.tail(1)["lineup_score"].values[0]

    for i in range(0, MAXGEN, 1):
        alpha_decay = round((i/MAXGEN)*POPSIZE)
        if alpha_decay < 1:
            alpha_decay = 1

        #############################
        new_high_score = population.head(1)["lineup_score"].values[0]
        new_low_score = population.tail(1)["lineup_score"].values[0]

        if(high_score != new_high_score or low_score != new_low_score):
            up = " ---"
            down = "--- "

            if high_score != new_high_score:
                up = " ^^^"

            if low_score != new_low_score:
                down = "^^^ "

            high_score = new_high_score
            low_score = new_low_score
            print(down + str(low_score) + " - " + str(high_score) + up)
        if(i % 500 == 0):
            write_population_to_csv(population)
            print("Iteration: ", i)
        ##############################

        #Select Random parent_one from population
        parent_one = select_random_lineup_from_population(population, alpha_decay)
        original_child_lineupid = parent_one["lineup_id"].values[0]

        child_lineup = parent_one

        #Apply mutations randomly
        child_lineup = apply_mutations(child_lineup, players_df, alpha_decay)

        random_lineup_id = random.getrandbits(32)
        child_lineup = child_lineup.assign(lineup_id=random_lineup_id)

        #Test child fitness
        child_cost = get_cost_from_lineup(child_lineup)
        child_score = get_score_from_lineup(child_lineup)

        child_lineup["lineup_score"] = child_score
        child_lineup["lineup_cost"] = child_cost

        temp = population[population.lineup_id != original_child_lineupid]
        temp = pd.concat([temp, child_lineup], sort=True)

        #if our final child is fitter than our worst in population, and meets requirements
        if (child_score > new_low_score and
            child_cost <= MAXCOST and
            not child_score in population["lineup_score"].unique() and
            enforce_max_exposure(temp)):

            #add child to population
            population = pd.concat([population, child_lineup], sort=True)

            #resort our population
            population = population.sort_values(by=['lineup_score', 'lineup_id'], ascending=False)

            #drop our lowest lineup
            #lowest_lineup_id = population.tail(1)["lineup_id"].values[0]
            lowest_lineup_id = original_child_lineupid
            population = population[population.lineup_id != lowest_lineup_id]
            population = population.sort_values(by=['lineup_score', 'lineup_id'], ascending=False)

    write_population_to_csv(population)

if __name__ == '__main__':
    main()
