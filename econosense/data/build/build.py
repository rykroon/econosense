import sys
import os
import acsbuild
import oesbuild
import geobuild
from partialdb import PartialDatabase

raw_data_path = 'data/build/rawdata'

try:
    year = sys.argv[1]
    try:
        int(year)
    except:
        print('Year must be numeric')
        sys.exit(0)

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

    try:
        os.mkdir(raw_data_path)
        print('Created directory ' + raw_data_path)
    except: pass

    path = os.path.join(raw_data_path,source)

    if source in ['geo','oes'] and not os.path.isdir(path):
        os.mkdir(path)

    partialdb = PartialDatabase()

    if source == 'geo':
        geobuild.partialdb = partialdb
        geobuild.main(year,path)

    partialdb = geobuild.partialdb

    if source == 'oes':
        oesbuild.partialdb = partialdb
        oesbuild.main(year,path)

    partialdb = oesbuild.partialdb
    if source == 'acs':
        acsbuild.partialdb = partialdb
        acsbuild.main(year)




#
