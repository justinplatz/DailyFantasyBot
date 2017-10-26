import urllib2
from bs4 import BeautifulSoup
import urllib2, sys

def scrapeDKIDs():
    url = "https://www.draftkings.com/bulklineup/getdraftablecsv?draftGroupId=16004"
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page,"lxml")

    arr = soup.text.split(",,,,,,,,,,")
    f = open('DKIds.csv', 'w')
    for i in arr:
        if(i.count("@") > 0):
            player_arr = i.split(",")
            line = player_arr[1] + "," + player_arr[2]
            f.write(line + '\n')


scrapeDKIDs()

def scrapePlayersFile():
    url = "http://rotoguru1.com/cgi-bin/fstats.cgi?pos=0&sort=4&game=p&colA=0&daypt=0&xavg=0&inact=0&maxprc=99999&outcsv=1"

    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page,"lxml")


    for i in soup.find_all('p'):
        if i.text.count(";") > 3:
            f = open('players.txt', 'w')
            arr = i.text.split("\n")
            arr.pop(0)
            for line in arr:
                if line.count(";") > 3:
                    if "D;" in line:
                        name = line.split(";")[2]
                        teamname = _switchDefenseCityForName(name)
                        line = line.replace(name, teamname)
                    f.write(line + '\n')
            f.close()

def _switchDefenseCityForName(city):
    if(city == 'Jacksonville'):
        return 'Jaguars'

    elif(city == 'Detroit'):
        return 'Lions'

    elif(city == 'Baltimore'):
        return 'Ravens'

    elif(city == 'LA Rams'):
        return 'Rams'

    elif(city == 'Washington'):
        return 'Redskins'

    elif(city == 'Pittsburgh'):
        return 'Steelers'

    elif(city == 'Philadelphia'):
        return 'Eagles'

    elif(city == 'Buffalo'):
        return 'Bills'

    elif(city == 'Kansas City'):
        return 'Chiefs'

    elif(city == 'Carolina'):
        return 'Panthers'

    elif(city == 'Cincinnati'):
        return 'Bengals'

    elif(city == 'Denver'):
        return 'Broncos'

    elif(city == 'Atlanta'):
        return 'Falcons'

    elif(city == 'Dallas'):
        return 'Cowboys'

    elif(city == 'Arizona'):
        return 'Cardinals'

    elif(city == 'Denver'):
        return 'Cowboys'

    elif(city == 'Tampa Bay'):
        return 'Buccaneers'

    elif(city == 'Houston'):
        return 'Texans'

    elif(city == 'Green Bay'):
        return 'Packers'

    elif(city == 'Chicago'):
        return 'Bears'

    elif(city == 'Oakland'):
        return 'Raiders'

    elif(city == 'LA Chargers'):
        return 'Chargers'

    elif(city == 'Indianapolis'):
        return 'Colts'

    elif(city == 'New York J'):
        return 'Jets'

    elif(city == 'Seattle'):
        return 'Seahawks'

    elif(city == 'Cleveland'):
        return 'Browns'

    elif(city == 'Minnesota'):
        return 'Vikings'

    elif(city == 'New Orleans'):
        return 'Saints'

    elif(city == 'New York G'):
        return 'Giants'

    elif(city == 'Tennessee'):
        return 'Titans'

    elif(city == 'San Francisco'):
        return '49ers'

    elif(city == 'New England'):
        return 'Patriots'

    elif(city == 'Miami'):
        return 'Dolphins'
    else:
        print city
        return