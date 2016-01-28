import json
import os, fnmatch

def findGame(offense, defense):
    rootdir = '/users/mmcvicar/Documents/Projects/FFBAWS/pbp_official/'

    for subdir, dirs, files in os.walk(rootdir):
        for file in fnmatch.filter(files, '*.txt'):
            json_data = open(rootdir + file).read()
            data = json.loads(json_data)

            if (data['summary']['home']['alias'] == offense and data['summary']['away']['alias'] == defense) or (data['summary']['home']['alias'] == defense and data['summary']['away']['alias'] == offense):
                print(file)

findGame('OAK', 'SD')
