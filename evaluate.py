import sys 
import json
from shapely import geometry, get_parts, unary_union
# from functions import 

if (len(sys.argv)>1 and sys.argv[1]):
    filename = sys.argv[1]
else: 
    filename = "1703797429.110371"
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
data = data[::-1]


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
        continue;
    try:
        rest = balcony.difference(roof)
        # rest = unary_union(block, rest)
    except:
        print("difference failed with") 
        print(polygonsIndex, roof)
        continue;
    
    if not rest.length:
        continue;
    
    # print("roof area", roof.area, "balcony", rest.area)

    # Save balconies sizes and number
    # if balcony.area>2:
    balconiesItems = get_parts(rest).tolist()
    # balconies = list(map(lambda x: x.area, balconiesItems))
    balconiesScore = 0
    print("Level:", polygonsIndex , "Blaconies", len(balconiesItems))
    for bal in balconiesItems:
        ok = ""
        if bal.area>2000:
            ok="OK"
        print("Area:", bal.area, ok)
        result.append({
                'area':  bal.area,
                # 'number': len(balconiesItems),
                # 'area': data[current].area,
                # 'scope':data[current].length
        })
    

# print(result)