def readFFSCSV():
  file = open('ffa.csv', 'r')

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
      for i in firstCol:
          col += i + " "
      if(" " in arr[0]):
          firstlast = arr[0].split(" ")
          fullname = firstlast[1] + ", " + firstlast[0]
          arr[0] = fullname
      if(arr not in list):
          list.append(arr)
      ffaPlayers[arr[0]] = {}
      ffaPlayers[arr[0]]["name"] = arr[0]
      ffaPlayers[arr[0]]["team"] = arr[1]
      ffaPlayers[arr[0]]["pos"] = arr[2]
      ffaPlayers[arr[0]]["points"] = arr[3]
      ffaPlayers[arr[0]]["ceil"] = arr[4]
      ffaPlayers[arr[0]]["floor"] = arr[5]
      ffaPlayers[arr[0]]["posRank"] = arr[6]

  for i in ffaPlayers:
      print ffaPlayers[i]

  return ffaPlayers

def main():
    ffaPlayers = readFFSCSV()


main()


