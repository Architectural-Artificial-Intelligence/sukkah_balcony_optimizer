import sys 
import json
import numpy as np


def fileWrite(f,txt):
    f.seek(0,2)
    f.write(txt+"\n\r")


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

filename = sys.argv[1]

input = open('generated/'+filename+'.json', 'r')

levels = json.load(input)

f = open('generated/'+filename+'.py', 'w')
fileWrite(f,"import rhinoscriptsyntax as rs")
fileWrite(f, "rs.EnableRedraw(False)")
fileWrite(f, "curves=[]")

y = 0
z = 0
for level in levels:
    data = json.loads(level)
    
    for polygons in data['coordinates']:

        # fileWrite(f, "strPath = rs.AddLine([0,0,0], [0,0,-"+str(z+3)+"])")
        fileWrite(f, "strPath = rs.AddLine([0,0,0], [0,0,-300])")

        if (hasattr(polygons[0][0], "__len__")):
            for polygon in polygons:
                polygon = setZ(polygon, z)

                fileWrite(f, "curve"+str(y)+" = rs.AddPolyline("+json.dumps(polygon)+")")
                # fileWrite(f, "rs.RebuildCurve ( curve"+str(y)+", degree=3, point_count=10)")
                fileWrite(f, "curves.append(curve"+str(y)+")")
                fileWrite(f, "rs.AddPlanarSrf(curve"+str(y)+")")
                fileWrite(f, "rs.ExtrudeCurve(curve"+str(y)+", strPath)")
                y+=1
        else:
            polygons = setZ(polygons, z)
            fileWrite(f, "curve"+str(y)+" = rs.AddPolyline("+json.dumps(polygons)+")")
            # fileWrite(f, "rs.RebuildCurve ( curve"+str(y)+", degree=3, point_count=10)")
            fileWrite(f, "curves.append(curve"+str(y)+")")
            fileWrite(f, "rs.AddPlanarSrf(curve"+str(y)+")")
            fileWrite(f, "rs.ExtrudeCurve(curve"+str(y)+", strPath)")
            y+=1
    z=z+300

fileWrite(f, "rs.EnableRedraw(True)")

f.close()