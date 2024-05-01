import sys 
import json
import numpy as np


def file_write(f,txt):
    f.seek(0,2)
    f.write(txt+"\n\r")


def polygon_rs_formatter(points):

    l = len(points)-1

    if points[0].x!= points[l].x or points[0].y!=points[l].y:
        points= np.append(points, points[0])
    ptsArr = []

    for point in points:
        ptsArr.append("(%s,%s,%s)"%(point.x,point.y,point.z))
    return ', '.join(ptsArr)

def setZ(points_array,z_height):
    rt_data = []
    for pt in points_array:
        pt.append(z_height)
        rt_data.append(pt)
    return rt_data

filename = sys.argv[1]

data = open('generated/'+filename+'.json', 'r')

levels = json.load(data)

f = open('generated/'+filename+'.py', 'w')
file_write(f,"import rhinoscriptsyntax as rs")
file_write(f, "rs.EnableRedraw(False)")
file_write(f, "curves=[]")

y = 0
z = 0
for level in levels:
    data = json.loads(level)
    
    for polygons in data['coordinates']:

        file_write(f, "strPath = rs.AddLine([0,0,0], [0,0,-300])")

        if (hasattr(polygons[0][0], "__len__")):
            for polygon in polygons:
                polygon = setZ(polygon, z)

                file_write(f, "curve"+str(y)+" = rs.AddPolyline("+json.dumps(polygon)+")")
                file_write(f, "curves.append(curve"+str(y)+")")
                file_write(f, "rs.AddPlanarSrf(curve"+str(y)+")")
                file_write(f, "rs.ExtrudeCurve(curve"+str(y)+", strPath)")
                y+=1
        else:
            polygons = setZ(polygons, z)
            file_write(f, "curve"+str(y)+" = rs.AddPolyline("+json.dumps(polygons)+")")
            file_write(f, "curves.append(curve"+str(y)+")")
            file_write(f, "rs.AddPlanarSrf(curve"+str(y)+")")
            file_write(f, "rs.ExtrudeCurve(curve"+str(y)+", strPath)")
            y+=1
    z=z+300

file_write(f, "rs.EnableRedraw(True)")

f.close()