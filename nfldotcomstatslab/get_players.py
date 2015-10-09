teams = {
    'ARI': '3800',
    'ATL': '0200',
    'BAL': '0325',
    'BUF': '0610',
    'CAR': '0750',
    'CHI': '0810',
    'CIN': '0920',
    'CLE': '1050',
    'DAL': '1200',
    'DEN': '1400',
    'DET': '1540',
    'GB' : '1800',
    'HOU': '2120',
    'IND': '2200',
    'JAX': '2250',
    'KAN': '2310',
    'MIA': '2700',
    'MIN': '3000',
    'NE' : '3200',
    'NO' : '3300',
    'NYJ': '3430',
    'NYG': '3410',
    'OAK': '2520',
    'PHI': '3700',
    'PIT': '3900',
    'SD' : '4400',
    'SF' : '4500',
    'SEA': '4600',
    'STL': '2510',
    'TB' : '4900',
    'TEN': '2100',
    'WAS': '5110'
}

positions = [
    'quarterback',
    'runningback',
    'widereceiver',
    'tightend',
    'kicker',
    'defender'
]

import requests
import json

url = 'http://www.nfl.com/ajax/statlabplayersbyteam?seasonId=2015&seasonType=REG&positionId={position}&teamId={team}'

players = {}
for position in positions:
    pos_players = {}
    for team in teams:
        r = requests.get(url.format(position=position,team=teams[team]))
        n = r.text.replace('\r','').replace('\n','').replace('"','').replace(':',',')
        x = n[27:].split(',')
        t = []

        for item in x:
            t.append(item.strip())
        pos_players[team] = dict(zip(t[::2],t[1::2]))

    players[position] = pos_players



with open('/users/mmcvicar/Documents/FFBAWS/nfldotcomstatslab/data.txt', 'w') as output:
        json.dump(players, output)




















