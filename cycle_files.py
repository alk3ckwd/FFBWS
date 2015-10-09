import os, fnmatch

count = 0
root_dir = '/Users/mmcvicar/Documents/FFBAWS/pbp_data/'

for subdir, dirs, files in os.walk(root_dir):
    for file in fnmatch.filter(files, '*.txt'):
        if 'injured' in open(root_dir + file).read():
            print(file)
            count += 1
            print(count)
            

import pandas

pandas.read_csv(
