import requests
import json
import os, fnmatch
import pandas as pd
import csv
from collections import defaultdict
import psycopg2 as psql
import numpy as np
from sqlalchemy import create_engine



location = 'Home'
save_path = ''

if location == 'Home':
    save_path = '/users/mmcvicar/Documents/Projects/FFBAWS/'
else:
    save_path = 'C:/Users/mmcvicar/Documents/FFBWS/FFBWS/'

refresh = input('Do you want to poll the latest data? (Y/N)')
if refresh == 'Y':

    key2 = 'w5tbrbj92uy7wkwv7wa4dmkf'
    

    schedule_url = 'https://api.sportsdatallc.org/nfl-ot1/games/2015/REG/schedule.json?api_key={key}'.format(key=key2)
    response = requests.get(url=schedule_url)
    sched_data = json.loads(response.text)
    with open(save_path + '2015_schedule_official.txt', 'w') as output:
        json.dump(sched_data, output)


    new_files = 0
    for week in sched_data['weeks']:
        for game in week['games']:
            if not os.path.isfile(save_path + 'pbp_data_official/gamepbp_{game}.txt'.format(game=game['id'])):
                if game['status'] == 'closed':
                    base_url = 'https://api.sportsdatallc.org/nfl-ot1/games/{gameID}/pbp.json?api_key={key}'.format(gameID=game['id'], key=key2)
                    r = requests.get(base_url)
                    data = json.loads(r.text)


                    with open(save_path + 'pbp_official/gamepbp_{game}.txt'.format(game=game['id']), 'w') as output:
                        json.dump(data, output)
                    new_files += 1

    print("Got {files} new files".format(files=new_files))

def pd_2_postgre(pdDataFrame, tableName):
    conn = psql.connect(database='ffbws', user='mmcvicar')
    cur = conn.cursor()
    cur.execute('DELETE FROM ' + tableName + ';')
    conn.commit()
    conn.close()
    engine = create_engine('postgresql://mmcvicar:@localhost/ffbws')
    pdDataFrame.to_sql(tableName, engine, if_exists='append')
    

def set_defense(data, offense):
    home = data['summary']['home']['alias']
    away = data['summary']['away']['alias']
    if offense == home:
        return away
    else:
        return home

def parse_pass_type(desc):
    if 'short right' in desc:
        return 'short right'
    elif 'short middle' in desc:
        return 'short middle'
    elif 'short left' in desc:
        return 'short left'
    elif 'deep right' in desc:
        return 'deep right'
    elif 'deep middle' in desc:
        return 'deep middle'
    elif 'deep left' in desc:
        return 'deep left'
    else:
        return ''

def parsePass(data, df_main, game_id, offense_team, defense_team, play_type, target_name, cmpt_flag, yards):
    
    for qtr in data['periods']:
        for drive in qtr['pbp']:
            if drive['type'] == "drive":
                for play in drive['events']:
                    if  'play_type' in play and play['play_type'] == "pass" and 'deleted' not in play:
                        game_id.append(data['id'])
                        #offense team
                        offense_team.append(play['start_situation']['possession']['alias'])
                        defense_team.append(set_defense(data, play['start_situation']['possession']['alias']))
                        #play_type
                        play_type.append(play['play_type'])
                        #completion flag
                        target_set = False
                        complete_flag_set = False
                        for stat in play['statistics']:
                            if stat['stat_type'] == 'pass':
                                
                                if 'complete' in stat and stat['complete'] == 1:
                                    cmpt_flag.append("C")
                                    yards.append(stat['yards'])
                                    complete_flag_set = True
                            #target_name
                            elif stat['stat_type'] == 'receive' and 'target' in stat and stat['target'] == 1:
                                target_name.append(stat['player']['name'])
                                target_set = True
                        if not target_set:
                            target_name.append(' ')
                        if not complete_flag_set:
                            cmpt_flag.append('I')
                            yards.append(0)

                        #pass type
                        pass_type.append(parse_pass_type(play['description']))
                        #print(game_id,offense_team,defense_team,play_type,cmpt_flag,target_name)
                        df_temp = pd.concat([pd.DataFrame(game_id, columns = ['game_id']),
                                             pd.DataFrame(offense_team, columns = ['offense_team']),
                                             pd.DataFrame(defense_team, columns = ['defense_team']),
                                             pd.DataFrame(play_type, columns = ['play_type']),
                                             pd.DataFrame(pass_type, columns = ['pass_type']),
                                             pd.DataFrame(target_name, columns = ['target_name']),
                                             pd.DataFrame(cmpt_flag, columns = ['cmpt_flag']),
                                             pd.DataFrame(yards, columns = ['yards'])], axis = 1)

                        df_main = pd.concat([df_main, df_temp], ignore_index=True)

                        del game_id[:]
                        del offense_team[:]
                        del defense_team[:]
                        del play_type[:]
                        del pass_type[:]
                        del target_name[:]
                        del cmpt_flag[:]
                        del yards[:]
    return df_main


if refresh == 'N':
    regenerate = input('Do you want to regenerate base files? (Y/N)')

if refresh == 'Y' or regenerate == 'Y':
    df_main = pd.DataFrame(columns = ['game_id', 'offense_team', 'defense_team', 'play_type', 'pass_type', 'target_name', 'cmpt_flag', 'yards'])
    df_full = pd.DataFrame(columns = ['game_id', 'offense_team', 'defense_team', 'play_type', 'pass_type', 'target_name', 'cmpt_flag', 'yards'])

    rootdir = save_path + 'pbp_official/'
    for subdir, dirs, files in os.walk(rootdir):
        for file in fnmatch.filter(files, '*.txt'):
            game_id = []
            offense_team = []
            defense_team = []
            play_type = []
            pass_type = []
            target_name = []
            cmpt_flag = []
            yards = []
            json_data = open(rootdir + file).read()
            data = json.loads(json_data)
            df_full = pd.concat([df_full, parsePass(data, df_main, game_id, offense_team, defense_team, play_type, target_name, cmpt_flag, yards)], ignore_index= True)
    df_full.to_csv(save_path + 'df_full.csv')
        

teams = pd.unique(df_full['offense_team'])
pass_types = pd.unique(df_full['pass_type'])


    offense_pass_PCT = {}
    
    for team in teams:
        part = {}
        for pass_type in pass_types:
            part[pass_type] = df_full[(df_full['offense_team'] == team) & (df_full['pass_type'] == pass_type) & (df_full['cmpt_flag'] == "C")].count()['play_type'] / df_full[(df_full['offense_team'] == team) & (df_full['pass_type'] == pass_type)].count()['play_type']
        offense_pass_PCT[team] = part

    offense_pass_yards = {}
    for team in teams:
        part = {}
        for pass_type in pass_types:
            part[pass_type] = df_full[(df_full['offense_team'] == team) & (df_full['pass_type'] == pass_type) & (df_full['cmpt_flag'] == "C")].mean()['yards']
        offense_pass_yards[team] = part

    offense_pass_attempts = {}
    for team in teams:
        part = {}
        for pass_type in pass_types:
            part[pass_type] = df_full[(df_full['offense_team'] == team) & (df_full['pass_type'] == pass_type)].count()['play_type']
        offense_pass_attempts[team] = part

    
    defense_pass_PCT = {}
    for team in teams:
        part = {}
        for pass_type in pass_types:
            part[pass_type] = df_full[(df_full['defense_team'] == team) & (df_full['pass_type'] == pass_type) & (df_full['cmpt_flag'] == "C")].count()['play_type'] / df_full[(df_full['defense_team'] == team) & (df_full['pass_type'] == pass_type)].count()['play_type']
        defense_pass_PCT[team] = part

    defense_pass_yards = {}
    for team in teams:
        part = {}
        for pass_type in pass_types:
            part[pass_type] = df_full[(df_full['defense_team'] == team) & (df_full['pass_type'] == pass_type) & (df_full['cmpt_flag'] == "C")].mean()['yards']
        defense_pass_yards[team] = part
    
    with open(save_path + 'Offense_Pass_PCT.txt', 'w') as output:
        json.dump(offense_pass_PCT, output)

    with open(save_path + 'Defense_Pass_PCT.txt', 'w') as output:
        json.dump(defense_pass_PCT, output)

    with open(save_path + 'Offense_Pass_yards.txt', 'w') as output:
        json.dump(offense_pass_yards, output)

    with open(save_path + 'Defense_Pass_yards.txt', 'w') as output:
        json.dump(defense_pass_yards, output)
    
df_full = pd.read_csv(save_path + 'df_full.csv', index_col=0)

teams = pd.unique(df_full['offense_team'])
pass_types = ['deep left', 'deep middle', 'deep right', 'short left', 'short middle', 'short right']

top_targets = df_full[['offense_team', 'pass_type', 'target_name']]
top_targets = top_targets.groupby(['offense_team', 'pass_type']).agg(lambda x:x.value_counts().index[0])


results = defaultdict(lambda: defaultdict(dict))
for index, value in top_targets.itertuples():
    for i, key in enumerate(index):
        if i == 0:
            nested = results[key]
        elif i == len(index) - 1:
            nested[key] = value
        else:
            nested = nested[key]

with open(save_path + 'Top_Targets.txt', 'w') as output:
    json.dump(results, output)

with open(save_path + 'teams.txt', mode='r') as infile:
    reader = csv.reader(infile)
    teamDict = {rows[0]:rows[1] for rows in reader}
    
def getTeamId(team2, teamDict):
    for index, team in teamDict.items():
        if team == team2:
            return index
 #target table               
targets = pd.read_json(save_path + 'Top_Targets.txt',orient='index')
for index, row in targets.iterrows():
    targets.loc[index, 'team_id'] = getTeamId(index, teamDict)
targets = targets.set_index(targets['team_id'])
targets.index = targets.index.astype(int)
targets.index += 1
targets = targets[['deep left', 'deep middle', 'deep right', 'short left', 'short middle', 'short right']]
targets.to_csv(save_path + 'targets.csv', index = True)

#offense pct table
off_pct = pd.read_json(save_path + 'Offense_Pass_PCT.txt',orient='index')
off_pct = np.round(off_pct*100,decimals=0)
for index, row in off_pct.iterrows():
    off_pct.loc[index, 'team_id'] = getTeamId(index, teamDict)
off_pct = off_pct.set_index(off_pct['team_id'])
off_pct.index = off_pct.index.astype(int)
off_pct.index += 1
off_pct = off_pct[['deep left', 'deep middle', 'deep right', 'short left', 'short middle', 'short right']]
off_pct.to_csv(save_path + 'off_pct.csv', index = True)

#offense yards table
off_yards = pd.read_json(save_path + 'Offense_Pass_yards.txt',orient='index')

for index, row in off_yards.iterrows():
    off_yards.loc[index, 'team_id'] = getTeamId(index, teamDict)
off_yards = off_yards.set_index(off_yards['team_id'])
off_yards.index = off_yards.index.astype(int)
off_yards.index += 1
off_yards = off_yards[['deep left', 'deep middle', 'deep right', 'short left', 'short middle', 'short right']]
off_yards.to_csv(save_path + 'off_yards.csv', index=True)

#defense pct table
def_pct = pd.read_json(save_path + 'Defense_Pass_PCT.txt',orient='index')
def_pct = np.round(def_pct*100,decimals=0)
def_pct['team_name'] = def_pct.index
for index, row in def_pct.iterrows():
    def_pct.loc[index, 'team_id'] = getTeamId(index, teamDict)
def_pct = def_pct.set_index(def_pct['team_id'])
def_pct.index = def_pct.index.astype(int)
def_pct.index += 1
def_pct = def_pct[['deep left', 'deep middle', 'deep right', 'short left', 'short middle', 'short right', 'team_name']]
def_pct.to_csv(save_path + 'def_pct.csv', index = True)

#defense yards table
def_yards = pd.read_json(save_path + 'Defense_Pass_yards.txt',orient='index')
def_yards['team_name'] = def_yards.index
for index, row in def_yards.iterrows():
    def_yards.loc[index, 'team_id'] = getTeamId(index, teamDict)
def_yards = def_yards.set_index(def_yards['team_id'])
def_yards.index = def_yards.index.astype(int)
def_yards.index += 1
def_yards = def_yards[['deep left', 'deep middle', 'deep right', 'short left', 'short middle', 'short right', 'team_name']]
def_yards.to_csv(save_path + 'def_yards.csv', index=True)



df_pct_full = pd.concat([off_pct, def_pct], axis=1)
pct_cols = [
    'team_name',
    'off_sl_pct',
    'off_sm_pct',
    'off_sr_pct',
    'off_ll_pct',
    'off_lm_pct',
    'off_lr_pct',
    'def_sl_pct',
    'def_sm_pct',
    'def_sr_pct',
    'def_ll_pct',
    'def_lm_pct',
    'def_lr_pct'
]
df_pct_full.columns = ['off_ll_pct', 'off_lm_pct', 'off_lr_pct', 'off_sl_pct', 'off_sm_pct', 'off_sr_pct',
               'def_ll_pct', 'def_lm_pct', 'def_lr_pct', 'def_sl_pct', 'def_sm_pct', 'def_sr_pct', 'team_name']

df_pct_full = df_pct_full[pct_cols]
df_pct_full.index.name = 'id'
df_pct_full.to_csv(save_path + 'stats.csv', index = True, float_format='%.0f')


df_yards_full = pd.concat([off_yards, def_yards], axis=1)
yards_cols = [
    'team_name',
    'off_sl_yards',
    'off_sm_yards',
    'off_sr_yards',
    'off_ll_yards',
    'off_lm_yards',
    'off_lr_yards',
    'def_sl_yards',
    'def_sm_yards',
    'def_sr_yards',
    'def_ll_yards',
    'def_lm_yards',
    'def_lr_yards'
]
df_yards_full.columns = ['off_ll_yards', 'off_lm_yards', 'off_lr_yards', 'off_sl_yards', 'off_sm_yards', 'off_sr_yards',
               'def_ll_yards', 'def_lm_yards', 'def_lr_yards', 'def_sl_yards', 'def_sm_yards', 'def_sr_yards', 'team_name']

df_yards_full = df_yards_full[yards_cols]
df_yards_full.index.name = 'id'
df_yards_full.to_csv(save_path + 'yards.csv', index = True, float_format='%.2f')

#pd_2_postgre(df_pct_full, 'football_stats')


    





















