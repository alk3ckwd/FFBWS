import json, csv
import pandas as pd
import numpy as np
from sklearn import linear_model

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

pass_types = ['deep left','deep middle', 'deep right', 'short left','short middle','short right']


def get_off_stats(team_id):
    return off_dict[team_id]
        
def get_def_stats(team_id):
    return def_dict[team_id]

def get_team_alias(team_id):
    return teamDict[team_id]

def get_off_game_results(game_id, team_id):
    off_game_results = []
    for pass_type in pass_types:
        cmpts = df_full[(df_full['offense_team'] == get_team_alias(team_id)) & (df_full['pass_type'] == pass_type) &
                       (df_full['cmpt_flag'] == "C") & (df_full['game_id'] == game_id)].count()['play_type']
        attmpts = df_full[(df_full['offense_team'] == get_team_alias(team_id)) & (df_full['pass_type'] == pass_type) &
                          (df_full['game_id'] == game_id)].count()['play_type']

        pct = cmpts/attmpts
        #print(type(pct))
        if np.isnan(pct):
            #print('fixing')
            pct = np.float64(0.0)
        off_game_results.append(pct*100)
    return off_game_results

full_data = []
for k,v in games_dict.items():
    temp = []
    temp.append(get_off_stats(v[0]) + get_def_stats(v[1]))
    temp.append(get_off_game_results(k, v[0]))
    full_data.append(temp)
    temp = []
    temp.append(get_off_stats(v[1]) + get_def_stats(v[0]))
    temp.append(get_off_game_results(k, v[1]))
    full_data.append(temp)


features = []
targets = []
for i in full_data:
    features.append(i[0])
    targets.append(i[1])

features_train = features[:500]
targets_train = targets[:500]
features_test = features[500:]
targets_test = targets[500:]

reg = linear_model.LinearRegression()
reg.fit(features_train, targets_train)
print('Coef', reg.coef_)
pred = reg.predict(features_test)
print('R: ', reg.score(pred, targets_test))

