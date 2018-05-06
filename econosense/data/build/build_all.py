import sys
import os
import acs_update
import oes_update
import geo_update

raw_data_path = 'appdata/update/rawdata'

try:
    year = sys.argv[1]
    try:
        int(year)
    except:
        print('Year must be numeric')

except:
    print("Must specify a year")
    sys.exit(0)


try:
    source = sys.argv[2]
    data_sources = list()
    data_sources.append(source)

except:
    data_sources = ['geo','oes','acs']


for source in data_sources:
    path = os.path.join(raw_data_path,source)

    if source in ['geo','oes'] and not os.path.isdir(path):
        os.mkdir(path)

    if source == 'geo': geo_update.main(year,path)
    if source == 'oes': oes_update.main(year,path)
    if source == 'acs': acs_update.main(year)
