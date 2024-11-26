import sys 
import json
import numpy as np
from shapely import geometry, get_parts, unary_union, to_geojson


def fileWrite(f,txt):
    f.seek(0,2)
    f.write(txt+"\n\r")


def readFile(fileName):

    input = open(fileName, 'r')
    levels = json.load(input)
    data = []
    for level in levels:
        poly = []
        polygon = geometry.shape(json.loads(level))
        data.append(polygon)
    return data

def polygonRSformatter(points):

    print(points)
    l = len(points)-1

    if points[0].x!= points[l].x or points[0].y!=points[l].y:
        points= np.append(points, points[0])
    ptsArr = []

    for point in points:
        ptsArr.append("(%s,%s,%s)"%(point.x,point.y,point.z))
    return ', '.join(ptsArr)

def setZ(pointsArray,z):
    data = []
    for pt in pointsArray:
        pt.append(z)
        data.append(pt)
    return data

def computeLevel(topLevels, balcony):

    level = []
    # Get roof
    try:
        roof = unary_union(topLevels)
    except:
        print("unary_union failed with") 
        return False;

    try:
        rest = balcony.difference(roof)

    except:
        print("difference failed with") 

    
    if not rest.length:
        return False;
    

    bal = []
    balconiesItems = get_parts(rest).tolist()
    for balcony in balconiesItems:
        if balcony.area>2000:
            bal.append(balcony.area)
    
    if (len(bal) <= 0):
        return False
    
    return balcony



filename = sys.argv[1]

levels = readFile('generated/'+filename+'.json')

# remove invalid levels
# start with roof
newBuilding = [levels[0:1:]]

#  loop without roof
for index in range(len(levels) - 1):
    topLevels = levels[0:index+1:]
    building = levels[index+1]
    
    if computeLevel(topLevels,building):
        print("Level "+ str(index)+" OK")
    else:
        print("Level "+ str(index)+" Fail")

# f = open('generated/'+filename+'.py', 'w')
# fileWrite(f,"import rhinoscriptsyntax as rs")
# fileWrite(f, "rs.EnableRedraw(False)")
# fileWrite(f, "curves=[]")

# y = 0
# z = 0

# for level in newBuilding:
#     data = to_geojson(level)
#     print("--")
#     print(data[0])

#     data= json.loads(data[0])
#     print(data)
    
#     for polygons in data['coordinates']:

#         # fileWrite(f, "strPath = rs.AddLine([0,0,0], [0,0,-"+str(z+3)+"])")
#         fileWrite(f, "strPath = rs.AddLine([0,0,0], [0,0,-300])")

#         if (hasattr(polygons[0][0], "__len__")):
#             for polygon in polygons:
#                 polygon = setZ(polygon, z)

#                 fileWrite(f, "curve"+str(y)+" = rs.AddPolyline("+json.dumps(polygon)+")")
#                 # fileWrite(f, "rs.RebuildCurve ( curve"+str(y)+", degree=3, point_count=10)")
#                 fileWrite(f, "curves.append(curve"+str(y)+")")
#                 fileWrite(f, "rs.AddPlanarSrf(curve"+str(y)+")")
#                 fileWrite(f, "rs.ExtrudeCurve(curve"+str(y)+", strPath)")
#                 y+=1
#         else:
#             polygons = setZ(polygons, z)
#             fileWrite(f, "curve"+str(y)+" = rs.AddPolyline("+json.dumps(polygons)+")")
#             # fileWrite(f, "rs.RebuildCurve ( curve"+str(y)+", degree=3, point_count=10)")
#             fileWrite(f, "curves.append(curve"+str(y)+")")
#             fileWrite(f, "rs.AddPlanarSrf(curve"+str(y)+")")
#             fileWrite(f, "rs.ExtrudeCurve(curve"+str(y)+", strPath)")
#             y+=1
#     z=z+300

# fileWrite(f, "rs.EnableRedraw(True)")

f.close()