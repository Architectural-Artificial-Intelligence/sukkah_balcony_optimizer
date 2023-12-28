import sys 
import json
from shapely import geometry, get_parts
# from functions import 

filename = sys.argv[1]

input = open('generated/'+filename+'.json', 'r')

levels = json.load(input)


data = []

for level in levels:
    poly = []
    polygon = geometry.shape(json.loads(level))
    data.append(polygon)

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
    # if balcony.area>2:
    balconiesItems = get_parts(balcony).tolist()
    # balconies = list(map(lambda x: x.area, balconiesItems))
    balconiesScore = 0
    print("Level:", polygonsIndex , "Blaconies", len(balconiesItems))
    for bal in balconiesItems:
        ok = ""
        if bal.area>200:
            ok="OK"
        print("Area:", bal.area, ok)
        result.append({
                'area':  bal.area,
                # 'number': len(balconiesItems),
                # 'area': data[current].area,
                # 'scope':data[current].length
        })
    

# print(result)