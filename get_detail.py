import requests
import json
import os, fnmatch
import time

key = ['urpsf9d8zrkrfca9r2e9mk5a', 'wbnwnxp5bhxevqxnagq3jaze', 'gdbp7pja3np4388tsenfnmjt', 'f38rfa5myeegprjxwa8c9rrq', 'qwagvmx9c9567unvywxy9qrp']

base_url = 'https://api.sportsdatallc.org/nfl-t1'

play_index = 0
key_index=0
rootdir = '/Users/mmcvicar/Documents/FFBAWS/pbp_data/'
for subdir, dirs, files in os.walk(rootdir):
        for file in fnmatch.filter(files, '*.txt'):
            json_data = open(rootdir + file).read()
            game_data = json.loads(json_data)
            print(file)
            for qtr in game_data['quarters']:
                    for drive in qtr['pbp']:
                            if drive['type'] == "drive":
                                    for play in drive['actions']:
                                        if not os.path.isfile('/users/mmcvicar/Documents/FFBAWS/play_detail/{play_id}.txt'.format(play_id=play['id'])):
                                            if 'details' in play:
                                                detail_url = play['details']
                                                print(base_url + detail_url + '?api_key=' + key[key_index])
                                                while True:
                                                    try:
                                                        r = requests.get(base_url + detail_url + '?api_key=' + key[key_index])
                                                        play_data = json.loads(r.text)
                                                        with open('/users/mmcvicar/Documents/FFBAWS/play_detail/{play_id}.txt'.format(play_id=play['id']), 'w') as output:
                                                            json.dump(play_data, output)
                                                        play_index += 1
                                                        time.sleep(1)
                                                        break
                                                    except:
                                                        
                                                        key_index += 1
                                                        print("trying new key:" + key[key_index])
