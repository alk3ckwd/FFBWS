import requests
import json


url = 'http://feeds.nfl.com/feeds-rs/playerSeasonStats/multi/bySeasonSeasonType/{playerIDs}/2015/REG.json?random=1442357789775&_jsonp=YUI.Env.JSONP.yui_3_10_3_1_1442357784164_8992'

file = open('/users/mmcvicar/documents/ffbaws/nfldotcomstatslab/data.txt').read()

players = json.loads(file)
player_string = ''
for pos in players.keys():
    if pos != 'defender':
        for team in players[pos]:
            for player in players[pos][team].keys():
                player_string += player + ','

player_string = player_string[:len(player_string)-1]

stats = requests.get(url.format(playerIDs=player_string))

print(stats.text[:100])
