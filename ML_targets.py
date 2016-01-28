import json, csv
import pandas as pd

location = 'Work'
save_path = ''

if location == 'Home':
    save_path = '/users/mmcvicar/Documents/Projects/FFBAWS/'
else:
    save_path = 'C:/Users/mmcvicar/Documents/FFBWS/FFBWS/'

f = open(save_path + '2015_schedule_official.txt').read()
sched = json.loads(f)

with open(save_path + 'teams.txt', mode='r') as infile:
    reader=csv.reader(infile)
    teamDict = {rows[0]:rows[1] for rows in reader}

teamDict.pop('')

teamDict = {int(k)+1:v for k,v in teamDict.items()}

def get_id(alias):
    for k,v in teamDict.items():
        if alias == v:
            return k
    return False

games_dict = {}
for w in sched['weeks']:
    for g in w['games']:
        g_id = g['id']
        h_id = get_id(g['home']['alias'])
        a_id = get_id(g['away']['alias'])
        games_dict[g_id] = [h_id, a_id]
        
with open(save_path + 'off_pct.csv', 'r') as f:
        reader = csv.reader(f)
        offense = list(reader)

offense = offense[1:]

off_dict = {}
for x in offense:
    off_dict[x[0]] = x[1:]

off_dict = {int(k):[float(i) for i in v] for k,v in off_dict.items()}

with open(save_path + 'def_pct.csv', 'r') as f:
        reader = csv.reader(f)
        defense = list(reader)

defense = defense[1:]

for x in defense:
    x = x.pop(-1)

def_dict = {}
for x in defense:
    def_dict[x[0]] = x[1:]
    
def_dict = {int(k):[float(i) for i in v] for k,v in def_dict.items()}


df_full = pd.read_csv(save_path + 'df_full.csv', index_col=0)

