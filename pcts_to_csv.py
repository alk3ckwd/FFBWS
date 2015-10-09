import json
import csv
import pandas as pd


#offense
offense = open('/Users/mmcvicar/Documents/FFBAWS/Offense_Pass_PCT.txt').read()
defense = open('/Users/mmcvicar/Documents/FFBAWS/Defense_Pass_PCT.txt').read()
off_data = json.loads(offense)
def_data = json.loads(defense)

team_name = []
off_short_left = []
off_short_middle = []
off_short_right = []
off_long_left = []
off_long_middle = []
off_long_right = []
def_short_left = []
def_short_middle = []
def_short_right = []
def_long_left = []
def_long_middle = []
def_long_right = []

for team in off_data:
        team_name.append(team)
        off_short_left.append(off_data[team]['Short Left'])
        off_short_middle.append(off_data[team]['Short Middle'])
        off_short_right.append(off_data[team]['Short Right'])
        off_long_left.append(off_data[team]['Long Left'])
        off_long_middle.append(off_data[team]['Long Middle'])
        off_long_right.append(off_data[team]['Long Right'])
        def_short_left.append(def_data[team]['Short Left'])
        def_short_middle.append(def_data[team]['Short Middle'])
        def_short_right.append(def_data[team]['Short Right'])
        def_long_left.append(def_data[team]['Long Left'])
        def_long_middle.append(def_data[team]['Long Middle'])
        def_long_right.append(def_data[team]['Long Right'])


off_short_left[:] = [round(x*100) for x in off_short_left]
off_short_middle[:] = [round(x*100) for x in off_short_middle]
off_short_right[:] = [round(x*100) for x in off_short_right]
off_long_left[:] = [round(x*100) for x in off_long_left]
off_long_middle[:] = [round(x*100) for x in off_long_middle]
off_long_right[:] = [round(x*100) for x in off_long_right]
def_short_left[:] = [round(x*100) for x in def_short_left]
def_short_middle[:] = [round(x*100) for x in def_short_middle]
def_short_right[:] = [round(x*100) for x in def_short_right]
def_long_left[:] = [round(x*100) for x in def_long_left]
def_long_middle[:] = [round(x*100) for x in def_long_middle]
def_long_right[:] = [round(x*100) for x in def_long_right]


stat_df = pd.concat([pd.DataFrame(off_short_left, columns = ['off_short_left']), 
                        pd.DataFrame(off_short_middle, columns = ['off_short_middle']), pd.DataFrame(off_short_right, columns = ['off_short_right']), 
                        pd.DataFrame(off_long_left, columns = ['off_long_left']), pd.DataFrame(off_long_middle, columns = ['off_long_middle']),
                        pd.DataFrame(off_long_right, columns = ['off_long_right']), pd.DataFrame(def_short_left, columns = ['def_short_left']), 
                        pd.DataFrame(def_short_middle, columns = ['def_short_middle']), pd.DataFrame(def_short_right, columns = ['def_short_right']), 
                        pd.DataFrame(def_long_left, columns = ['def_long_left']), pd.DataFrame(def_long_middle, columns = ['def_long_middle']),
                        pd.DataFrame(def_long_right, columns = ['def_long_right']), pd.DataFrame(team_name, columns = ['team_name'])], axis=1)

team_list = pd.DataFrame(team_name, columns = ['team_name'])
team_list = team_list.sort(['team_name'])
team_list = team_list.reset_index(drop=True)
team_list.to_csv('/Users/mmcvicar/Documents/FFBAWS/teams.txt', index = True)

stat_df = stat_df.sort(['team_name'])
stat_df = stat_df.reset_index(drop=True)
stat_df.to_csv('/Users/mmcvicar/Documents/FFBAWS/stats_csv.txt', index = True)
