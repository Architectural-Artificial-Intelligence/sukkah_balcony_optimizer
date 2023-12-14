import sys 
import json
import functools 
from shapely import geometry,Polygon, get_parts
from functions import fileWrite, polygonRSformatter

filename = sys.argv[1]

input = open('generated/'+filename+'.json', 'r')

levels = json.load(input)


data = []


for level in levels:
    poly = []
    for pt in level:
        poly.append(geometry.shape(pt))
    data.append(Polygon(poly))

result =[]
# convert to polygons


# array of the floors, from the top
floorStack = [data[len(data)-1]]

#  run on all floors, beside the roof.
for polygonsIndex in range(len(data)-1):
    current = len(data) - polygonsIndex-1

    balcony = data[polygonsIndex]

        # this calculates the polygon difference
    for currentBlaconyIndex in range(len(floorStack)):
        try:
            balcony = balcony.difference(floorStack[currentBlaconyIndex])

            if balcony.is_empty:
                break;
        except:
            exce = 1

    floorStack.append(data[current])


    # Save balconies sizes and number
    if balcony.area>2:
        balconiesItems = get_parts(balcony).tolist()
        # balconies = list(map(lambda x: x.area, balconiesItems))
        balconiesScore = 0
        for bal in balconiesItems:
            if (bal.area >=2):
                balconiesScore+1
        result.append({
                'balconies':  balconiesScore,
                # 'number': len(balconiesItems),
                # 'area': data[current].area,
                # 'scope':data[current].length
        })

print(result)