from bs4 import BeautifulSoup
import urllib.request
import json
import requests
import pandas as pd

from config import draft_kings_url, projected_ownership_url

def scrape_dk_ids_to_df():
    page = urllib.request.urlopen(draft_kings_url).read()
    soup = BeautifulSoup(page, "lxml")


    valid_pos = ["QB", "RB", "WR", "TE", "DST", "K"]
    arr = soup.text.split(",,,,,,,,,,")

    players = []
    for i in arr:
        if(i.count("@") > 0):
            player_arr = i.split(",")
            position = player_arr[0]
            if position not in valid_pos:
                continue

            name = player_arr[2].strip()
            id = player_arr[3]
            salary = int(player_arr[5])
            team = player_arr[7]

            player = [name, id, position, salary, team]
            players.append(player)

    df = pd.DataFrame(players, columns=['Name', 'ID', 'Position', 'Salary', 'Team'])
    return df


def get_projected_ownership_to_df():

    r = requests.get(projected_ownership_url)
    arr = json.loads(r.content)

    df = pd.DataFrame(arr, columns=['Ceiling', 'DKPts', 'Floor', 'Game', 'Id',
                                    'ImpPts', 'MaxExp', 'MinExp', 'Name', 'OU',
                                    'Opp', 'Position', 'ProjOwn', 'Salary', 'Spread',
                                    'TeamAbbrev', 'TimeRank', 'Val', 'Venue'])
    return df

if __name__ == '__main__':
    get_projected_ownership_to_df()
