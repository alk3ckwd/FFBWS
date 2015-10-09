import requests
import json
import os, fnmatch
import pandas as pd
from collections import defaultdict

refresh = input('Do you want to refresh the data? (Y/N)')
if refresh == 'Y':

    key2 = 'wbnwnxp5bhxevqxnagq3jaze'
    

    schedule_url = 'https://api.sportsdatallc.org/nfl-ot1/games/2015/REG/schedule.json?api_key={key}'.format(key=key2)
    response = requests.get(url=schedule_url)
    sched_data = json.loads(response.text)
    with open('/users/mmcvicar/Documents/FFBAWS/2015_schedule_official.txt', 'w') as output:
        json.dump(sched_data, output)


    new_files = 0
    for week in sched_data['weeks']:
        for game in week['games']:
            if not os.path.isfile('/users/mmcvicar/Documents/FFBAWS/pbp_data_official/gamepbp_{game}.txt'.format(game=game['id'])):
                if game['status'] == 'closed':
                    base_url = 'https://api.sportsdatallc.org/nfl-ot1/games/{gameID}/pbp.json?api_key={key}'.format(gameID=game['id'], key=key2)
                    r = requests.get(base_url)
                    data = json.loads(r.text)


                    with open('/users/mmcvicar/Documents/FFBAWS/pbp_official/gamepbp_{game}.txt'.format(game=game['id']), 'w') as output:
                        json.dump(data, output)
                    new_files += 1

    print("Got {files} new files".format(files=new_files))

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

def parsePass(data, df_main, offense_team, defense_team, play_type, target_name, cmpt_flag):
    for qtr in data['periods']:
        for drive in qtr['pbp']:
            if drive['type'] == "drive":
                for play in drive['events']:
                    if  'play_type' in play and play['play_type'] == "pass" and 'deleted' not in play:
                        #offense team
                        #print(data['id'],play['id'])
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
                                    complete_flag_set = True
                            #target_name
                            elif stat['stat_type'] == 'receive' and 'target' in stat and stat['target'] == 1:
                                target_name.append(stat['player']['name'])
                                target_set = True
                        if not target_set:
                            target_name.append(' ')
                        if not complete_flag_set:
                            cmpt_flag.append('I')

                        #pass type
                        pass_type.append(parse_pass_type(play['description']))
                        #print(play['id'],offense_team,defense_team,play_type,cmpt_flag,target_name)
                        df_temp = pd.concat([pd.DataFrame(offense_team, columns = ['offense_team']), pd.DataFrame(defense_team, columns = ['defense_team']),
                                            pd.DataFrame(play_type, columns = ['play_type']), pd.DataFrame(pass_type, columns = ['pass_type']),
                                            pd.DataFrame(target_name, columns = ['target_name']), pd.DataFrame(cmpt_flag, columns = ['cmpt_flag'])], axis = 1)

                        df_main = pd.concat([df_main, df_temp], ignore_index=True)

                        del offense_team[:]
                        del defense_team[:]
                        del play_type[:]
                        del pass_type[:]
                        del target_name[:]
                        del cmpt_flag[:]
    return df_main


df_main = pd.DataFrame(columns = ['offense_team', 'defense_team', 'play_type', 'pass_type', 'target_name', 'cmpt_flag'])
df_full = pd.DataFrame(columns = ['offense_team', 'defense_team', 'play_type', 'pass_type', 'target_name', 'cmpt_flag'])

game = 0
rootdir = 'C:/Users/mmcvicar/Documents/FFBWS/FFBWS/pbp_official/'
for subdir, dirs, files in os.walk(rootdir):
    for file in fnmatch.filter(files, '*.txt'):
        offense_team = []
        defense_team = []
        play_type = []
        pass_type = []
        target_name = []
        cmpt_flag = []
        json_data = open(rootdir + file).read()
        data = json.loads(json_data)
        df_full = pd.concat([df_full, parsePass(data, df_main, offense_team, defense_team, play_type, target_name, cmpt_flag)], ignore_index= True)
        game += 1

teams = pd.unique(df_full['offense_team'])
pass_types = pd.unique(df_full['pass_type'])



offense_pass_PCT = {}
for team in teams:
    part = {}
    for pass_type in pass_types:
        part[pass_type] = df_full[(df_full['offense_team'] == team) & (df_full['pass_type'] == pass_type) & (df_full['cmpt_flag'] == "C")].count()['play_type'] / df_full[(df_full['offense_team'] == team) & (df_full['pass_type'] == pass_type)].count()['play_type']
    offense_pass_PCT[team] = part

defense_pass_PCT = {}
for team in teams:
    part = {}
    for pass_type in pass_types:
        part[pass_type] = df_full[(df_full['defense_team'] == team) & (df_full['pass_type'] == pass_type) & (df_full['cmpt_flag'] == "C")].count()['play_type'] / df_full[(df_full['defense_team'] == team) & (df_full['pass_type'] == pass_type)].count()['play_type']
    defense_pass_PCT[team] = part

with open('C:/users/mmcvicar/Documents/FFBWS/FFBWS/Offense_Pass_PCT.txt', 'w') as output:
    json.dump(offense_pass_PCT, output)

with open('C:/users/mmcvicar/Documents/FFBWS/FFBWS/Defense_Pass_PCT.txt', 'w') as output:
    json.dump(defense_pass_PCT, output)


off_pct = pd.read_json('C:/Users/mmcvicar/Documents/FFBWS/FFBWS/Offense_Pass_PCT.txt',orient='index')
off_pct = off_pct[['deep left', 'deep middle', 'deep right', 'short left', 'short middle', 'short right']]

def_pct = pd.read_json('C:/Users/mmcvicar/Documents/FFBWS/FFBWS/Defense_Pass_PCT.txt',orient='index')
def_pct = def_pct[['deep left', 'deep middle', 'deep right', 'short left', 'short middle', 'short right']]

results = defaultdict(lambda: defaultdict(dict))
for index, value in test.itertuples():
    for i, key in enumerate(index):
        if i == 0:
            nested = results[key]
        elif i == len(index) - 1:
            nested[key] = value
        else:
            nested = nested[key]

top_targets = df_full[['offense_team', 'pass_type', 'target_name']]
top_targets.groupby(['offense_team', 'pass_type']).agg(lambda x:x.value_counts().index[0])
