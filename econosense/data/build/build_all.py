import sys
import os
import acs_build
import oes_build
import geo_build

raw_data_path = 'data/build/rawdata'

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
    print(source)
    path = os.path.join(raw_data_path,source)

    if source in ['geo','oes'] and not os.path.isdir(path):
        os.mkdir(path)

    if source == 'geo': geo_update.main(year,path)
    if source == 'oes': oes_update.main(year,path)
    if source == 'acs': acs_update.main(year)
