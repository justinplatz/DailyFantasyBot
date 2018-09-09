import random
from copy import deepcopy
import math
from web import scrapePlayersFile, scrapeDKIDs

MAXCOST = 50000
MAXGEN = 250000
POPSIZE = 100

def main():

    scrapePlayersFile()
    scrapeDKIDs()

    listOfQBs = []
    listOfRBs = []
    listOfWRs = []
    listOfTEs = []
    listOfFXs = []
    listOfDEs = []

    file = open('input/players.txt', 'r')

    players = readFileAndReturnPlayersDict(file)


    for player in players:
        if(players[player]["pos"] == "QB"):
            listOfQBs.append(players[player])

        elif(players[player]["pos"] == "RB"):
            listOfRBs.append(players[player])
            listOfFXs.append(players[player])

        elif(players[player]["pos"] == "WR"):
            listOfWRs.append(players[player])
            listOfFXs.append(players[player])

        elif(players[player]["pos"] == "TE"):
            listOfTEs.append(players[player])
            listOfFXs.append(players[player])

        elif(players[player]["pos"] == "D"):
            listOfDEs.append(players[player])

        else:
            print players[player]

    listOfQBs = sorted(listOfQBs, key=lambda k: k['posRank'])
    listOfRBs = sorted(listOfRBs, key=lambda k: k['posRank'])
    listOfWRs = sorted(listOfWRs, key=lambda k: k['posRank'])
    listOfTEs = sorted(listOfTEs, key=lambda k: k['posRank'])
    listOfFXs = sorted(listOfFXs, key=lambda k: k['posRank'])
    listOfDEs = sorted(listOfDEs, key=lambda k: k['posRank'])

    population = generateRandomLineups(deepcopy(listOfQBs),deepcopy(listOfRBs),deepcopy(listOfWRs),deepcopy(listOfTEs),deepcopy(listOfFXs),deepcopy(listOfDEs), MAXCOST, POPSIZE)
    population = sorted(population, key=lambda k: k['score'])
    highScore = population[POPSIZE]["score"]
    lowScore = population[0]["score"]
    for i in range(0,MAXGEN,1):

        #############################
        #Used for printing high Score and iterations
        if(highScore != population[POPSIZE]["score"] or lowScore != population[0]["score"]):
            up = " ---"
            if highScore != population[POPSIZE]["score"]:
                up = " ^^^"

            down = "--- "
            if lowScore != population[0]["score"]:
                down = "^^^ "

            highScore = population[POPSIZE]["score"]
            lowScore = population[0]["score"]
            print down + str(population[0]["score"]) + " - " + str(highScore) + up

            makeCSVUsingPopulation(population)


        if(i % 1000 == 0):
            print "Iteration: ",i
        ##############################

        cutoff = int(math.ceil(POPSIZE * .1))
        #Select Random parent1 from population
        parent1 = selectRandomFromList(deepcopy(population[:cutoff]))
        parent1lineup = parent1["lineup"]

        #select Random parent2 from population
        parent2 = selectRandomFromList(deepcopy(population[:-cutoff]))

        while parent1 == parent2:
            parent2 = selectRandomFromList(deepcopy(population))

        parent2lineup = parent2["lineup"]

        ###############################
        # Create Child
        # - Either Splice and combine parents to form child (90%)
        # - Or use highest ranked lineup as child (10%)
        randomInt = random.randint(0,9)
        if(randomInt < 9):
            ###############################
            # 1. Make child
            # Splice and combine lineups
            childLineup = spliceAndCombineParents(parent1lineup, parent2lineup)

            ###############################
            # 2. Check child
            # Constraint checking of child
            # checklineup for duplicate players
            childLineup = removeDuplicatesFromLineup(deepcopy(childLineup), listOfQBs,listOfRBs,listOfWRs,listOfTEs)

            # check if lineup too expensive
            childCost = getCostFromLineup(deepcopy(childLineup))

            if(childCost > MAXCOST):
                continue
        else:
            childLineup = population[POPSIZE]["lineup"]
            childCost = getCostFromLineup(deepcopy(childLineup))

        ###############################
        #get score from child lineup
        childScore = deepcopy(getScoreFromLineup(deepcopy(childLineup)))

        #set the child's properties
        child = {}
        child["cost"] = childCost
        child["lineup"] = childLineup
        child["score"] = childScore

        #if we already have this child
        if(child in population or childScore <= population[0]["score"]):
           #make a new random child
           child = generateRandomChild(listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfFXs,listOfDEs, MAXCOST)

           #Check if lineup too expensive
           cost = getCostFromLineup(deepcopy(child["lineup"]))
           if(cost > MAXCOST):
                continue
           # checklineup for duplicate players
           child["lineup"] = removeDuplicatesFromLineup(deepcopy(childLineup), listOfQBs,listOfRBs,listOfWRs,listOfTEs)

        #if our child was worse than our others, apply mutations
        mutate = random.randint(0,1)
        if(mutate == 0):

           randomInt = random.randint(0,4)

           # 0,1 = 40% chance
           if(randomInt < 2):
                #make a new random swap
                child = swapPlayerForRandom(deepcopy(child["lineup"]),listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs)
           # 3,4 = 40% chance
           elif(randomInt == 3 or randomInt == 4):
                #swap for a higher pos rank
                child = swapForHigherPosRank(deepcopy(child["lineup"]),listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs)
           # 5 = 20% chance
           else:
                #swap for a higher pos rank
                child = swapForLowerPosRank(deepcopy(child["lineup"]),listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs)

           #checklineup for duplicate players
           childLineup = removeDuplicatesFromLineup(child["lineup"], listOfQBs,listOfRBs,listOfWRs,listOfTEs)

           #Check if lineup too expensive
           cost = getCostFromLineup(deepcopy(childLineup))
           if(cost > MAXCOST):
                continue

        #if our final child is better than our worst
        if(child["score"] > population[0]["score"] and child["cost"] < MAXCOST and childLineupNotInPopulation(child,population)):
            #set our worst to be our child
            population[0] = child

            #population = removeOverlyAppearingPlayersFromPopulation(deepcopy(population), listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs, MAXCOST, players)

            #resort our population
            population = sorted(deepcopy(population), key=lambda k: k['score'])


def childLineupNotInPopulation(child, population):

    childPlayerMap = {}
    for i in child["lineup"]:
        childPlayerMap[i["name"]] = 1

    for p in population:
        comparePlayerMap = {}
        for x in p["lineup"]:
            comparePlayerMap[x["name"]] = 1

        if comparePlayerMap == childPlayerMap:
            return False

    return True

def makeCSVUsingPopulation(population):
    outfile = open('output/output.txt', 'w')


    nameToIDMap = {}
    file = open('input/DKIds.csv', 'r')
    for line in file:
        arr = line.replace("\r","").replace("\n","").replace('\t','').split(",")
        if(arr[1].endswith(" ")):
            arr[1] = arr[1][:-1]
        nameToIDMap[arr[1]] = arr[0]



    # for item in population:
    #     outfile.write("%s\n" % item)

    namesNotFound = []
    #for i in population:
    for i in range(len(population)-1, 0, -1):
        line = ""
        count = 0
        lineup = population[i]["lineup"]
        for p in lineup:
            count += 1
            name = p["name"]
            nameArr = name.split(",")

            if len(nameArr) > 1:
                fullName = str(nameArr[1])[1:] + " " + nameArr[0]
            else:
                fullName = nameArr[0]

            if fullName in nameToIDMap:
                name = nameToIDMap[fullName]
            else:
                if fullName not in namesNotFound:
                    namesNotFound.append(fullName)

            line += (name + ", " if count != len(lineup) else name)

        outfile.write("%s\n" % line)

    outfile.write("\n")

    outfile.write("RANGE: \n")
    string = str(population[0]["score"]) + " - " + str(population[POPSIZE]["score"])
    outfile.write("%s\n" % string)
    outfile.write("\n")

    outfile.write("NAMES NOT FOUND: \n")
    for i in namesNotFound:
        outfile.write("%s\n" % i)





#currently not being used
def removeOverlyAppearingPlayersFromPopulation(population,listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs, MAXCOST, players):

    done = True

    playerToLineupCountMap = buildPlayerCountMap(population, players)

    for x in playerToLineupCountMap:
        name = x[0]
        pos = x[1]
        if len(playerToLineupCountMap[x]) > 12:
            done = False

            childToFix = population[playerToLineupCountMap[x][0]]

            for i in childToFix["lineup"]:
                #find the player to fix
                if i["name"] == name:

                    i = swapForHigherPlayer(x[0],x[1],-4,listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs)


    return population

def swapForHigherPlayer(name,pos,val,listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs):

    #If we are swapping QB
    if(pos == "QB"):
       #Look at list of QBs
       for i in range(0,len(listOfQBs),1):
           #Find our current QB
           if listOfQBs[i]["name"] == name:
               #If he is not the best QB
               if i > 0:
                   return listOfQBs[i-val]
               else:
                   return listOfQBs[i]

    elif(pos == "RB"):
       #Look at list of RBs
       for i in range(0,len(listOfRBs),1):
           #Find our current RB
           if listOfRBs[i]["name"] == name:
               #If he is not the best RB
               if i > 0:
                   return listOfRBs[i-val]
               else:
                   return listOfRBs[i]

    elif(pos == "WR"):
       #Look at list of WRs
       for i in range(0,len(listOfWRs),1):
           #Find our current RB
           if listOfWRs[i]["name"] == name:
               #If he is not the best WR
               if i > 0:
                   return listOfWRs[i-val]
               else:
                   return listOfWRs[i]

    elif(pos == "TE"):
       #Look at list of TE
       for i in range(0,len(listOfTEs),1):
           #Find our current TE
           if listOfTEs[i]["name"] == name:
               #If he is not the best TE
               if i > 0:
                   return listOfTEs[i-val]
               else:
                   return listOfTEs[i]

    elif(pos == "D"):
       #Look at list of DE
       for i in range(0,len(listOfDEs),1):
           #Find our current DE
           if listOfDEs[i]["name"] == name:
               #If he is not the best DE
               if i > 0:
                   return listOfDEs[i-val]
               else:
                   return listOfDEs[i]

def buildPlayerCountMap(population,players):
    # Make the initial player to count map
    playerToLineupCountMap = {}

    for x in players:
        playerToLineupCountMap[players[x]["name"]] = []

    for i in range(0,len(population),1):
        for p in range(0,len(population[i]["lineup"]),1):
            name = (population[i]["lineup"][p]["name"],population[i]["lineup"][p]["pos"])
            if name not in playerToLineupCountMap:
                playerToLineupCountMap[name] = [i]
            else:
                playerToLineupCountMap[name].append(i)
    return playerToLineupCountMap

def spliceAndCombineParents(parent1, parent2):

    child = parent1

    for i in range(0, len(parent1), 1):
        parent = random.randint(0,1)

        if parent == 0:
            child[i] = parent1[i]
        elif parent == 1:
            child[i] = parent2[i]

    return child


def generateRandomLineups(listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfFXs,listOfDEs, MAXCOST, POPSIZE):
    population = []
    for i in range(0,POPSIZE+1,1):
        child = generateRandomChild(listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfFXs,listOfDEs, MAXCOST)
        population.append(child)
    return population

def swapForHigherPosRank(lineup,listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs):
    #Pick rancom split number
    randomInt = random.randint(0,8)

    #If we are swapping QB
    if(lineup[randomInt]["pos"] == "QB"):
       #Look at list of QBs
       for i in range(0,len(listOfQBs),1):
           #Find our current QB
           if listOfQBs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the best QB
               if i > 0:
                   #Set our QB to be a higher PosRank
                   lineup[randomInt] = listOfQBs[i-1]

    elif(lineup[randomInt]["pos"] == "RB"):
       #Look at list of RBs
       for i in range(0,len(listOfRBs),1):
           #Find our current RB
           if listOfRBs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the best RB
               if i > 0:
                   #Set our RB to be a higher PosRank
                   lineup[randomInt] = listOfRBs[i-1]

    elif(lineup[randomInt]["pos"] == "WR"):
       #Look at list of WRs
       for i in range(0,len(listOfWRs),1):
           #Find our current RB
           if listOfWRs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the best WR
               if i > 0:
                   #Set our WR to be a higher PosRank
                   lineup[randomInt] = listOfWRs[i-1]

    elif(lineup[randomInt]["pos"] == "TE"):
       #Look at list of TE
       for i in range(0,len(listOfTEs),1):
           #Find our current TE
           if listOfTEs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the best TE
               if i > 0:
                   #Set our TE to be a higher PosRank
                   lineup[randomInt] = listOfTEs[i-1]

    elif(lineup[randomInt]["pos"] == "D"):
       #Look at list of DE
       for i in range(0,len(listOfDEs),1):
           #Find our current DE
           if listOfDEs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the best DE
               if i > 0:
                   #Set our DE to be a higher PosRank
                   lineup[randomInt] = listOfDEs[i-1]

    lineup = removeDuplicatesFromLineup(lineup,listOfQBs, listOfRBs, listOfWRs, listOfTEs)
    score = getScoreFromLineup(lineup)
    cost = getCostFromLineup(lineup)

    child = {}
    child["cost"] = cost
    child["lineup"] = lineup
    child["score"] = score

    return child

def swapForLowerPosRank(lineup,listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs):
    #Pick rancom split number
    randomInt = random.randint(0,8)

    #If we are swapping QB
    if(lineup[randomInt]["pos"] == "QB"):
       #Look at list of QBs
       for i in range(0,len(listOfQBs),1):
           #Find our current QB
           if listOfQBs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the worst QB
               if i+1 < len(listOfQBs):
                   #Set our QB to be a lower PosRank
                   lineup[randomInt] = listOfQBs[i+1]

    elif(lineup[randomInt]["pos"] == "RB"):
       #Look at list of RBs
       for i in range(0,len(listOfRBs),1):
           #Find our current RB
           if listOfRBs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the worst RB
               if i+1 < len(listOfRBs):
                   #Set our RB to be a lower PosRank
                   lineup[randomInt] = listOfRBs[i+1]

    elif(lineup[randomInt]["pos"] == "WR"):
       #Look at list of WRs
       for i in range(0,len(listOfWRs),1):
           #Find our current RB
           if listOfWRs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the worst WR
               if i+1 < len(listOfWRs):
                   #Set our WR to be a lower PosRank
                   lineup[randomInt] = listOfWRs[i+1]

    elif(lineup[randomInt]["pos"] == "TE"):
       #Look at list of TE
       for i in range(0,len(listOfTEs),1):
           #Find our current TE
           if listOfTEs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the worst TE
               if i+1 < len(listOfTEs):
                   #Set our TE to be a lower PosRank
                   lineup[randomInt] = listOfTEs[i+1]

    elif(lineup[randomInt]["pos"] == "D"):
       #Look at list of DE
       for i in range(0,len(listOfDEs),1):
           #Find our current DE
           if listOfDEs[i]["name"] == lineup[randomInt]["name"]:
               #If he is not the worst DE
               if i+1 < len(listOfDEs):
                   #Set our DE to be a lower PosRank
                   lineup[randomInt] = listOfDEs[i+1]

    lineup = removeDuplicatesFromLineup(lineup,listOfQBs, listOfRBs, listOfWRs, listOfTEs)
    score = getScoreFromLineup(lineup)
    cost = getCostFromLineup(lineup)

    child = {}
    child["cost"] = cost
    child["lineup"] = lineup
    child["score"] = score

    return child

def swapPlayerForRandom(lineup,listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfDEs):
    #Pick rancom split number
    randomInt = random.randint(0,8)
    if(lineup[randomInt]["pos"] == "QB"):
       lineup[randomInt] = selectRandomFromList(listOfQBs)
    elif(lineup[randomInt]["pos"] == "RB"):
       lineup[randomInt] = selectRandomFromList(listOfRBs)
    elif(lineup[randomInt]["pos"] == "WR"):
       lineup[randomInt] = selectRandomFromList(listOfWRs)
    elif(lineup[randomInt]["pos"] == "TE"):
       lineup[randomInt] = selectRandomFromList(listOfTEs)
    elif(lineup[randomInt]["pos"] == "D"):
       lineup[randomInt] = selectRandomFromList(listOfDEs)

    lineup = removeDuplicatesFromLineup(lineup,listOfQBs, listOfRBs, listOfWRs, listOfTEs)
    score = getScoreFromLineup(lineup)
    cost = getCostFromLineup(lineup)

    child = {}
    child["cost"] = cost
    child["lineup"] = lineup
    child["score"] = score

    return child

def generateRandomChild(listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfFXs,listOfDEs, MAXCOST):
    #generate random lineup
    lineup = generateRandomLineup(listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfFXs,listOfDEs, MAXCOST)
    #remove duplicates
    lineup = removeDuplicatesFromLineup(deepcopy(lineup), listOfQBs,listOfRBs,listOfWRs,listOfTEs)
    #get the cost
    cost = getCostFromLineup(deepcopy(lineup))
    #get the score
    score = getScoreFromLineup(deepcopy(lineup))
    #return the child
    child = {}
    child["lineup"] = lineup
    child["cost"] = cost
    child["score"] = score
    return child

def removeDuplicatesFromLineup(lineup, listOfQBs,listOfRBs,listOfWRs,listOfTEs):
    #Check for duplicate RBS
    while(lineup[1] == lineup[2] or
          lineup[1] == lineup[7] or
          lineup[2] == lineup[7]):

        lineup[1] = selectRandomFromList(listOfRBs)
        lineup[2] = selectRandomFromList(listOfRBs)

    # while(lineup[2] == lineup[7] or lineup[2] == lineup[1]):
    #     lineup[2] = selectRandomFromList(listOfRBs)

    #Check for duplicate WRs
    while(lineup[3] == lineup[4] or
          lineup[3] == lineup[5] or
          lineup[3] == lineup[7] or
          lineup[4] == lineup[5] or
          lineup[4] == lineup[7] or
          lineup[5] == lineup[7]):

        lineup[3] = selectRandomFromList(listOfWRs)
        lineup[4] = selectRandomFromList(listOfWRs)
        lineup[5] = selectRandomFromList(listOfWRs)

    # while(lineup[4] == lineup[5] or lineup[4] == lineup[7] or lineup[3] == lineup[4]):
    #     lineup[4] = selectRandomFromList(listOfWRs)
    # while(lineup[5] == lineup[7]):
    #     lineup[5] = selectRandomFromList(listOfWRs)

    #check fpr duplicate TEs
    while(lineup[6] == lineup[7]):
        lineup[6] = selectRandomFromList(listOfTEs)

    return lineup


def generateRandomLineup(listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfFXs,listOfDEs, MAXCOST):
    qb = selectRandomFromList(listOfQBs)
    rb1 = selectRandomFromList(listOfRBs)
    rb2 = selectRandomFromList(listOfRBs)
    wr1 = selectRandomFromList(listOfWRs)
    wr2 = selectRandomFromList(listOfWRs)
    wr3 = selectRandomFromList(listOfWRs)
    te = selectRandomFromList(listOfTEs)
    flex = selectRandomFromList(listOfFXs)
    de = selectRandomFromList(listOfDEs)

    lineup = [qb,rb1,rb2,wr1,wr2,wr3,te,flex,de]
    cost = getCostFromLineup(deepcopy(lineup))

    if(cost > MAXCOST):
        lineup = generateRandomLineup(listOfQBs,listOfRBs,listOfWRs,listOfTEs,listOfFXs,listOfDEs, MAXCOST)

    return lineup

def getScoreFromLineup(lineup):
    score = 0
    for player in lineup:
        try:
            score += (1.0)*player["points"] + (.05)*player["ceil"] + (.25)*player["floor"]
        except:
            score += 0
    return score

def getCostFromLineup(lineup):
    cost = 0
    for player in lineup:
        cost += player["salary"]
    return cost

def selectRandomFromList(list):
    random.shuffle(list)
    return list[0]

def readFileAndReturnPlayersDict(file):
    ffaPlayers = readFFSCSV()

    players = {}
    for line in file:
        #0-GID;
        #1-Pos;
        #2-Name;
        #3-Team;
        #4-Opponent;
        #5-Home/Away;
        #6-Salary;
        #7-Salary Change;
        #8-Points;
        #9 GP;
        #10-Pts/Game;
        #11-Pts/G/$;
        #12-Pts/G(alt);
        #13-Bye week;
        arr = line.split(";")

        pos = arr[1]
        name = arr[2]
        team = arr[3]
        salary = arr[6]
        players[name] = {}
        players[name]["name"] = name
        players[name]["team"] = team
        players[name]["salary"] = float(salary)
        players[name]["pos"] = pos

        if(_ignoreTeamsNotPlayingDuringTimeWindow(players[name]["team"])):
            del players[name]
            continue

        if(name in ffaPlayers):
            players[name]["points"] = float(ffaPlayers[name]["points"])
            players[name]["posRank"] = ffaPlayers[name]["posRank"]
            players[name]["ceil"] = ffaPlayers[name]["ceil"]
            players[name]["floor"] = ffaPlayers[name]["floor"]
        else:
            del players[name]

    return players

def readFFSCSV():
  file = open('input/FFA.csv', 'r')

  ffaPlayers = {}
  list = []
  for line in file:
      arr = line.replace("\r","").replace("\n","").split(",")
      #0-Player
      #1-Team
      #2-Pos
      #3-Points
      #4-Ceiling
      #5-Floor
      #6-Pos Rank
      firstCol = arr[0].split(" ")
      firstCol.pop()
      col = ""
      if(arr[2] != "DST"):
          for i in firstCol:
              col += i + " "
          if(" " in arr[0]):
              firstlast = arr[0].split(" ")
              fullname = firstlast[1] + ", " + firstlast[0]
              arr[0] = fullname
      if(arr[0].endswith(" ")):
          arr[0] = arr[0][:-1]
      if(arr not in list):
          list.append(arr)
      ffaPlayers[arr[0]] = {}
      ffaPlayers[arr[0]]["name"] = arr[0]
      ffaPlayers[arr[0]]["team"] = arr[1]
      ffaPlayers[arr[0]]["pos"] = arr[2]
      ffaPlayers[arr[0]]["points"] = float(arr[3])
      ffaPlayers[arr[0]]["ceil"] = float(arr[4])
      ffaPlayers[arr[0]]["floor"] = float(arr[5])
      ffaPlayers[arr[0]]["posRank"] = int(arr[6])

  return ffaPlayers

def _ignoreTeamsNotPlayingDuringTimeWindow(city):

    if(city == 'phi'):
        return True
    elif(city == 'atl'):
        return True

    elif(city == 'nyj'):
        return True
    elif(city == 'det'):
        return True

    elif(city == 'lar'):
        return True
    elif(city == 'oak'):
        return True

    else:
        return False

main()
