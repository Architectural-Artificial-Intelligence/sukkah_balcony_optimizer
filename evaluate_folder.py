import sys 
import json
import glob
import csv
import statistics
from shapely import geometry, get_parts, unary_union
# from functions import 

def read_file(file_name):

    input = open(file_name, 'r')
    levels = json.load(input)
    data = []
    for level in levels:
        poly = []
        polygon = geometry.shape(json.loads(level))
        data.append(polygon)
    return data


def compute(data):
    # array of the floors, from the top
    data = data[::-1]

    levels = []
    #  run on all floors, beside the roof.
    for polygonsIndex in range(len(data)-1):
        balcony = data[polygonsIndex+1]

        # Get roof
        try:
            topLevels = data[0:polygonsIndex+1:]
            roof = unary_union(topLevels)
            # roof = unary_union(block, roof)
        except:
            print("unary_union failed with") 
            print(balcony[0:polygonsIndex:])
            continue
        try:
            rest = balcony.difference(roof)
            # rest = unary_union(block, rest)
        except:
            print("difference failed with") 
            print(polygonsIndex, roof)
            continue

        if not rest.length:
            continue

        bal = []
        balconiesItems = get_parts(rest).tolist()
        for balcony in balconiesItems:
            if balcony.area>2000:
                bal.append(balcony.area)
        levels.append(bal)

    # create counts
    valid_balconies = 0
    valid_levels = 0
   
    for level in levels:
         # 1. Count number of valid balconies
        for balcony in level:
            valid_balconies=valid_balconies+1
        
        # 2. How many levels with at least one balcony
        if len(level)>0:
            valid_levels=valid_levels+1

    # 3. avarge size of balcony
    size = sum(sum(levels, []))
    stdev = statistics.stdev(sum(levels, []))
    return [valid_balconies, valid_levels,size,stdev];

files = glob.glob("./generated/*")
with open('./output.csv', newline='', mode='w', encoding='UTF8') as f:
    writer = csv.writer(f)

    for file in files:
        if not file.endswith('.json'):
            continue
        levels = read_file(file)
        o = compute(levels)
        writer.writerow(o)
            