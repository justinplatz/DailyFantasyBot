draft_kings_url = "https://www.draftkings.com/bulklineup/getdraftablecsv?draftGroupId=29777"
projected_ownership_url = "https://ui.dfsforecast.com/players/4?slate=Main&site=dk&"

ffa_file = "input/ffa_customrankings2019.csv"

output_df_file = "output/output_population.csv"
output_players_file = "output/output_all_players.csv"
output_dk_file = "output/output_dk.csv"
output_ex_file = "output/output_ex.csv"


MAXCOST = 50000
MAXGEN = 50000
POPSIZE = 20
MAXEXPOSURE = 0.25

def get_score_from_player(player):
    score = 0

    ceil  = float(player["upper"].values[0])
    floor = float(player["lower"].values[0])
    points = float(player["points"].values[0])
    tier = float(player["tier"].values[0])
    posrank = float(player["positionECR"].values[0])
    projected_ownership = float(player["projected_ownership"].values[0])
    spread = float(player["ptSpread"].values[0])

    score += (1.500) * points \
          + (1.750) * ceil \
          + (0.875) * floor \
          - (0.125) * tier \
          - (0.250) * posrank \
          - (0.250) * spread \
          + (1.500) * projected_ownership

    return score