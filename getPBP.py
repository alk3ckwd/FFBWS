import requests
import json
import os, fnmatch
import pandas as pd

refresh = input('Do you want to refresh the data? (Y/N)')
if resfresh = 'Y':

    key = 'urpsf9d8zrkrfca9r2e9mk5a'

    schedule_url = 'https://api.sportsdatallc.org/nfl-t1/2014/REG/schedule.json?api_key={key}'.format(key=key)

    response = requests.get(url=schedule_url)

    sched_data = json.loads(response.text)

    with open('/users/mmcvicar/Documents/FFBAWS/schedule.txt', 'w') as output:
      json.dump(sched_data, output)


    game_index = 0
    for week in sched_data['weeks']:
        for game in week['games']:
            base_url = 'https://api.sportsdatallc.org/nfl-t1/2014/{week}/{away}/{home}/pbp.json?api_key={key}'.format(week=week['number'], away=game['away'], home=game['home'], key=key)

            r = requests.get(base_url)
            data = json.loads(r.text)


            with open('/users/mmcvicar/Documents/FFBAWS/pbp_data/gamepbp_{game}.txt'.format(game=game_index), 'w') as output:
                json.dump(data, output)

            game_index += 1
        

def set_defense(data, offense):
    home = data['home_team']['id']
    away = data['away_team']['id']
    if offense == home:
        return away
    else:
        return home

def parsePass(data, df_main, offense_team, defense_team, play_type, target_name, cmpt_flag):
    for qtr in data['quarters']:
        for drive in qtr['pbp']:
            if drive['type'] == "drive":
                for play in drive['actions']:
                    if 'play_type' in play and play['play_type'] == "pass" and 'distance' in play and 'direction' in play:
                        #print(play['sequence'])
                        #offense team
                        offense_team.append(play['participants'][0]['team'])
                        defense_team.append(set_defense(data, play['participants'][0]['team']))
                        #play_type
                        play_type.append(play['play_type'])
                        #completion flag
                        if 'incomplete' in play['summary'] or 'intercepted' in play['summary']:
                            cmpt_flag.append("I")
                        else:
                            cmpt_flag.append("C")

                        #pass type
                        pass_type.append(play['distance'] + " " + play['direction'])

                        #target name
                        
                        if len(play['participants']) > 1:
                            target_set = False
                            for player in play['participants'][1:]:
                                if player['team'] == play['participants'][0]['team']:
                                    if not target_set:
                                        target_name.append(player['name'])
                                        target_set = True
                            if not target_set:
                                target_name.append(' ')
                        else:
                            target_name.append(' ')
                                                      
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

def passes:
    df_main = pd.DataFrame(columns = ['offense_team', 'defense_team', 'play_type', 'pass_type', 'target_name', 'cmpt_flag'])
    df_full = pd.DataFrame(columns = ['offense_team', 'defense_team', 'play_type', 'pass_type', 'target_name', 'cmpt_flag'])

    game = 0
    rootdir = '/Users/mmcvicar/Documents/FFBAWS/pbp_data/'
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

    with open('/users/mmcvicar/Documents/FFBAWS/Offense_Pass_PCT.txt', 'w') as output:
    	json.dump(offense_pass_PCT, output)

    with open('/users/mmcvicar/Documents/FFBAWS/Defense_Pass_PCT.txt', 'w') as output:
    	json.dump(defense_pass_PCT, output)


    top_targets = df_full[['offense_team', 'pass_type', 'target_name']]
    top_targets.groupby(['offense_team', 'pass_type']).agg(lambda x:x.value_counts().index[0])
 
