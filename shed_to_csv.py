import json
import csv
import pandas as pd

f = open('/Users/mmcvicar/Documents/FFBAWS/nfl_sched.txt').read()
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
	home_name = game['home']
	away_name = game['away']
	
	for index, team in teamDict.items():
		if team == home_name:
			home_team.append(index)
		if team == away_name:
			away_team.append(index)

for weeks in sched['weeks']:
	for game in weeks['games']:
		week.append(weeks['number'])
		getTeamId(game, teamDict)
		humidity.append(game['weather']['humidity'])
		temp.append(game['weather']['temperature'])
		condition.append(game['weather']['condition'])
		wind_speed.append(game['weather']['wind']['speed'])
		wind_dir.append(game['weather']['wind']['direction'])

		venue_type.append(game['venue']['type'])
		venue_surface.append(game['venue']['surface'])

sched_df = pd.concat([pd.DataFrame(week, columns = ['week']), 
				pd.DataFrame(humidity, columns = ['humidity']), pd.DataFrame(temp, columns = ['temp']), pd.DataFrame(condition, columns = ['condition']),
				pd.DataFrame(wind_speed, columns = ['wind_speed']), pd.DataFrame(wind_dir, columns = ['wind_dir']),
				pd.DataFrame(venue_type, columns = ['venue_type']), pd.DataFrame(venue_surface, columns = ['venue_surface']),
				pd.DataFrame(away_team, columns = ['away_team']), pd.DataFrame(home_team, columns = ['home_team'])], axis = 2)




sched_df.to_csv('/Users/mmcvicar/Documents/FFBAWS/nflsched_csv.txt', index = True)


		