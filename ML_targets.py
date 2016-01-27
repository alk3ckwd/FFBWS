import json, csv

f = open('/users/mmcvicar/documents/projects/ffbaws/2015_schedule_official.txt').read()
sched = json.loads(f)

with open('/users/mmcvicar/documents/projects/ffbaws/teams.txt', mode='r') as infile:
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
        
