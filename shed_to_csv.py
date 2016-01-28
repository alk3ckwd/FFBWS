import json
import csv
import pandas as pd
import numpy

location = 'Work'
save_path = ''

if location == 'Home':
    save_path = '/users/mmcvicar/Documents/Projects/FFBAWS/'
else:
    save_path = 'C:/Users/mmcvicar/Documents/FFBWS/FFBWS/'

f = open(save_path + '2015_schedule_official.txt').read()
sched = json.loads(f)

with open(save_path + 'teams.txt', mode='r') as infile:
    reader = csv.reader(infile)
    teamDict = {rows[0]:rows[1] for rows in reader}


game_id= []
home_team = []
away_team = []
week = []
#humidity = []
#temp = []
#condition = []
#wind_speed = []
#wind_dir = []
venue_type = []
venue_surface=[]

def getTeamId(game, teamDict):
    home_name = game['home']['alias']
    away_name = game['away']['alias']
    
    for index, team in teamDict.items():
        if team == home_name:
            home_team.append(int(index)+1)
        if team == away_name:
            away_team.append(int(index)+1)

def setWeather(weather,roof):
        if 'dome' not in roof:
                condition.append(weather[:weather.index('Temp')-1])
                
                
                wind_speed.append(weather[weather.index(weather[weather.index('Wind')+6:][:weather[weather.index('Wind')+6:].index(' ')])+len(weather[weather.index('Wind')+6:][:weather[weather.index('Wind')+6:].index(' ')])+1:][:-4])
                wind_dir.append(weather[weather.index('Wind')+6:][:weather[weather.index('Wind')+6:].index(' ')])
                if 'Humidity' in weather:
                        humidity.append(weather[weather.index('Humidity')+10:weather.index('%')])
                        temp.append(weather[weather.index('Temp:')+6:weather.index('Humidity')-5])
                else:
                        if 'rain' in weather[:weather.index('Temp')-1]:
                                humidity.append(100)
                        else:
                                humidity.append('')
                        temp.append(weather[weather.index('Temp:')+6:weather.index(',')-3])
                
        else:
                condition.append('')
                humidity.append(numpy.nan)
                temp.append(numpy.nan)
                wind_speed.append(numpy.nan)
                wind_dir.append('')

        
for weeks in sched['weeks']:
    for game in weeks['games']:
        if game['status'] == 'closed':
                game_id.append(game['id'])
                week.append(weeks['sequence'])
                getTeamId(game, teamDict)
                #print(game['id'])
                venue_type.append(game['venue']['roof_type'])
                venue_surface.append(game['venue']['surface'])
##                if 'weather' not in game:
##                        weather = 'dome'
##                else:
##                        weather = game['weather']
##
##                setWeather(weather, game['venue']['roof_type'])
        

sched_df = pd.concat([pd.DataFrame(game_id, columns = ['game_id']), pd.DataFrame(week, columns = ['week']), 
  #              pd.DataFrame(humidity, columns = ['humidity']), pd.DataFrame(temp, columns = ['temp']), pd.DataFrame(condition, columns = ['condition']),
 #               pd.DataFrame(wind_speed, columns = ['wind_speed']), pd.DataFrame(wind_dir, columns = ['wind_dir']),
                pd.DataFrame(venue_type, columns = ['venue_type']), pd.DataFrame(venue_surface, columns = ['venue_surface']),
                pd.DataFrame(away_team, columns = ['away_team_id']), pd.DataFrame(home_team, columns = ['home_team_id'])], axis = 2)

sched_df.index.name = 'id'
sched_df.index = sched_df.index.astype(int)
sched_df.index += 1

sched_df.to_csv(save_path + 'nflsched_official.csv', index = True)


		
