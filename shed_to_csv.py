import json
import csv
import pandas as pd

f = open('/Users/mmcvicar/Documents/FFBAWS/2015_schedule_official.txt').read()
sched = json.loads(f)

with open('/Users/mmcvicar/Documents/FFBAWS/teams.txt', mode='r') as infile:
    reader = csv.reader(infile)
    teamDict = {rows[0]:rows[1] for rows in reader}



home_team = []
away_team = []
week = []
humidity = []
temp = []
condition = []
wind_speed = []
wind_dir = []
venue_type = []
venue_surface=[]

def getTeamId(game, teamDict):
    home_name = game['home']['alias']
    away_name = game['away']['alias']
    
    for index, team in teamDict.items():
        if team == home_name:
            home_team.append(index)
        if team == away_name:
            away_team.append(index)

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
                                humidity.append(' ')
                        temp.append(weather[weather.index('Temp:')+6:weather.index(',')-3])
                
        else:
                condition.append(' ')
                humidity.append(' ')
                temp.append(' ')
                wind_speed.append(' ')
                wind_dir.append(' ')

        
for weeks in sched['weeks']:
    for game in weeks['games']:
        if game['status'] == 'closed':
                week.append(weeks['sequence'])
                getTeamId(game, teamDict)
                print(game['id'])
                venue_type.append(game['venue']['roof_type'])
                venue_surface.append(game['venue']['surface'])
                if 'weather' not in game:
                        weather = 'dome'
                else:
                        weather = game['weather']

                setWeather(weather, game['venue']['roof_type'])
        

sched_df = pd.concat([pd.DataFrame(week, columns = ['week']), 
                pd.DataFrame(humidity, columns = ['humidity']), pd.DataFrame(temp, columns = ['temp']), pd.DataFrame(condition, columns = ['condition']),
                pd.DataFrame(wind_speed, columns = ['wind_speed']), pd.DataFrame(wind_dir, columns = ['wind_dir']),
                pd.DataFrame(venue_type, columns = ['venue_type']), pd.DataFrame(venue_surface, columns = ['venue_surface']),
                pd.DataFrame(away_team, columns = ['away_team']), pd.DataFrame(home_team, columns = ['home_team'])], axis = 2)




sched_df.to_csv('/Users/mmcvicar/Documents/FFBAWS/nflsched_csv_official.txt', index = True)


		
