import random
import pandas as pd
import math

from web import get_projected_ownership_to_df

from config import POPSIZE, ffa_file, get_score_from_player, output_df_file, output_dk_file, output_ex_file, output_players_file

def write_players_to_csv(players_df):
    players_df.to_csv(output_players_file, sep='\t', encoding='utf-8')

def write_population_to_csv(population):
    population.to_csv(output_df_file, sep='\t', encoding='utf-8')

    counts = (population['player'].value_counts() / POPSIZE)
    counts.to_csv(output_ex_file, sep='\t', encoding='utf-8')

    outfile = open(output_dk_file, 'w')
    lineup_ids = population["lineup_id"].unique()
    for lineup_id in lineup_ids:
        row = ""
        lineup = population[population["lineup_id"] == lineup_id]
        positions = ["QB", "RB1", "RB2", "WR1", "WR2", "WR3", "TE", "FLEX", "DST"]
        for pos in positions:
            player = lineup.loc[lineup["lineup_position"] == pos]
            name = player["player"].values[0]
            id = player["ID"].values[0]
            row += name + "(" + id + ")" + ", "
        row = row[:-2]
        outfile.write("%s\n" % row)


def merge_dk_ids_and_ffa_stats(dk_players_df):

    ffa_df = read_ffa_to_df_()

    # Restrict the search space by limiting position ranks
    ffa_df = ffa_df[
        ((ffa_df["position"] == "QB") & (ffa_df["positionRank"] <= 16)) |
        ((ffa_df["position"] == "RB") & (ffa_df["positionRank"] <= 32)) |
        ((ffa_df["position"] == "WR") & (ffa_df["positionRank"] <= 48)) |
        ((ffa_df["position"] == "TE") & (ffa_df["positionRank"] <= 16)) |
        ((ffa_df["position"] == "DST") & (ffa_df["positionRank"] <= 16))
    ]

    projected_ownership_df = get_projected_ownership_to_df()

    print("The following players are in DK and not in FFA")
    for index, row in dk_players_df.iterrows():
        name = row["Name"]
        name = name + " "
        name = name.replace(" III ","").replace(" II ","").replace(" V ","").replace(" Jr. ","").replace(" IV ","").replace("'","").strip()

        #Get the row for this player from FFA DF
        try:
            ffa_player = ffa_df.loc[ffa_df['player'] == name]
            ffa_player_row = ffa_player.index[0]

            #Set the ID to be ID from DK
            ffa_df.loc[ffa_player_row, "ID"] = row["ID"]
            ffa_df.loc[ffa_player_row, "salary"] = row["Salary"]

            if math.isnan(ffa_player["positionECR"].values[0]):
                ffa_df.loc[ffa_player_row, "positionECR"] = 100
        except:
            print(name)
            continue

        try:
            # Get the row for this player from FFA DF
            projected_ownership_player = projected_ownership_df.loc[projected_ownership_df['Name'] == name]
            projected_ownership = projected_ownership_player["ProjOwn"].values[0]
        except:
            projected_ownership = 100

        ffa_df.loc[ffa_player_row, "projected_ownership"] = projected_ownership

        # normalize values which are used for scoring
        ffa_df["upper"] = ffa_df["upper"].rank(pct=True)
        ffa_df["lower"] = ffa_df["lower"].rank(pct=True)
        ffa_df["points"] = ffa_df["points"].rank(pct=True)
        ffa_df["tier"] = ffa_df["tier"].rank(pct=True)
        ffa_df["positionECR"] = ffa_df["positionECR"].rank(pct=True)
        ffa_df["projected_ownership"] = ffa_df["projected_ownership"].rank(pct=True)
        ffa_df["ptSpread"] = ffa_df["ptSpread"].rank(pct=True)




        # Add score to players_df
        score = get_score_from_player(ffa_df.loc[ffa_df['player'] == name])
        ffa_df.loc[ffa_player_row, "score"] = score



    ffa_df = ffa_df.drop('playerId', 1)
    ffa_df = ffa_df.drop('bye', 1)
    ffa_df = ffa_df.drop('age', 1)
    ffa_df = ffa_df.drop('overallECR', 1)
    ffa_df = ffa_df.drop('exp', 1)
    ffa_df = ffa_df.drop('sdPts', 1)
    ffa_df = ffa_df.drop('sdRank', 1)
    ffa_df = ffa_df.drop('sleeper', 1)

    ffa_df = ffa_df.dropna(subset=["ID"])

    ffa_df = ffa_df.sort_values(by=['score'], ascending=False)

    return ffa_df

def read_ffa_to_df_():
    df = pd.read_csv(ffa_file)
    return df

if __name__ == '__main__':
    df = read_ffa_to_df_()
    print(df)