import json
import os, fnmatch
import pandas as pd

def set_defense(data, offense):
    home = data['home_team']['id']
    away = data['away_team']['id']
    if offense == home:
        return away
    else:
        return home

def get_yftd(play, offense):
    if offense == play['side']:
        return play['yard_line']
    else:
        return 100 - play['yard_line']

def get_formation(play):
    if 'formation' in play:
        return play['formation']
    elif play['play_type'] == 'kick':
        return 'Kick off'
    elif play['play_type'] == 'extrapoint':
        return 'Extrapoint'
    elif play['play_type'] == 'punt':
        return 'Punt'
    elif play['play_type'] == 'fieldgoal':
        return 'Fieldgoal'
    elif play['play_type'] == 'penalty':
        return 'Penalty - no play'
    else:
        return 'Under center'


def get_penalty_team(desc):
    if 'Penalty on' in desc:
        start = desc.index('Penalty on ') + 11
        temp = desc[start:]
        end = temp.index(' ')
        return desc[start:end]

def parsePass(play):
    


def parseRun(play):
    direction = play['direction']
    rusher_name = play['participants'][0]
    yards_gained = yards_gained
    

    
game = 0
rootdir = '/Users/mmcvicar/Documents/FFBAWS/pbp_data/'

play_types = []

for subdir, dirs, files in os.walk(rootdir):
    for file in fnmatch.filter(files, '*.txt'):
        json_data = open(rootdir + file).read()
        data = json.loads(json_data)
        for qtr in data['quarters']:
            for drive in qtr['pbp']:
                #if 'type' in drive:
                    if drive['type'] == 'drive':
                        for play in drive['actions']:
                            if play['type'] == 'play':
                                #print(play)
                                game_id = [data['id']]
                                quarter = [qtr['number']]
                                offense = [drive['team']]
                                defense = [set_defense(data, offense)]
                                clock_min = [play['clock']]
                                clock_sec = [play['clock']]
                                if 'down' in play:
                                    down = [play['down']]
                                    yftd = [get_yftd(play, offense)]
                                    yfd = [play['yfd']]
                                raw_description = [play['summary']]
                                formation = [get_formation(play)]
                                play_type = [play['play_type']]
                                if 'official' in play:
                                    official = [False]
                                    pen_team = [get_penalty_team(play['summary'])]
                                else:
                                    official = [True]
                                if play_type == 'pass':
                                    parsePass(play)
                                elif play_type == 'run':
                                    parseRun(play)
                                
                        
                                
                            

