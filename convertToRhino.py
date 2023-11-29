import sys 
import json
from functions import fileWrite, polygonRSformatter

filename = sys.argv[1]

input = open('generated/'+filename+'.json', 'r')

levels = json.load(input)

f = open('generated/'+filename+'.py', 'w')
fileWrite(f,"import rhinoscriptsyntax as rs")
fileWrite(f, "rs.EnableRedraw(False)")
fileWrite(f, "curves=[]")
fileWrite(f, "strPath = rs.AddLine([0,0,0], [0,0,3])")

y = 0
for level in levels:

    fileWrite(f, "curve"+str(y)+" = rs.AddPolyline(["+level+"])")
    # fileWrite(f, "rs.RebuildCurve ( curve"+str(y)+", degree=3, point_count=10)")
    fileWrite(f, "curves.append(curve"+str(y)+")")
    fileWrite(f, "rs.ExtrudeCurve(curve"+str(y)+", strPath)")
    y+=1

fileWrite(f, "rs.EnableRedraw(True)")

f.close()