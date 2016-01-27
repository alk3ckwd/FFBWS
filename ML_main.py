from sklearn.linear_model import LinearRegression
import csv
import numpy as np



with open('/users/mmcvicar/documents/projects/ffbaws/off_pct.csv', 'r') as f:
        reader = csv.reader(f)
        offense = list(reader)

offense = offense[1:]

off_dict = {}
for x in offense:
    off_dict[x[0]] = x[1:]

off_dict = {int(k):[float(i) for i in v] for k,v in off_dict.items()}

with open('/users/mmcvicar/documents/projects/ffbaws/def_pct.csv', 'r') as f:
        reader = csv.reader(f)
        defense = list(reader)

defense = defense[1:]

for x in defense:
    x = x.pop(-1)

def_dict = {}
for x in defense:
    def_dict[x[0]] = x[1:]
    
def_dict = {int(k):[float(i) for i in v] for k,v in def_dict.items()}

g = open('/users/mmcvicar/documents/projects/FFBAWS/nflsched_official.csv')
schedule = csv.reader(g)
next(schedule)
games = []
for row in schedule:
    matchup = [int(row[5]), int(row[4])]
    games.append(matchup)

features = []
for game in games:
        first = off_dict[game[0]]
        second = def_dict[game[1]]
        combo1 = first + second
        features.append(combo1)
        first = off_dict[game[1]]
        second = def_dict[game[0]]
        combo2 = first + second
        features.append(combo2)

features = np.array(features)


