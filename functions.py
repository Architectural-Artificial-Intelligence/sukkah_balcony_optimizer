import pygad
import numpy as np
import random
import math
import time
import json
from shapely import Polygon, Point, get_num_geometries, get_parts

# =================================================
# functions
# =================================================

def generateRandom(boundingPolygon, howManyPoints, levels, levelOffset):
    points = []
    (minx, miny, maxx, maxy) = boundingPolygon.bounds
    for level in range(levels):
        z = levelOffset*level
        sides = 4
        pointsInSide = int(howManyPoints/4)
        x = y = 10
        for side in range(sides):
            for current in range(pointsInSide):
                if side==0:
                    x=x+2
                if side==1:
                    y=y+2
                if side==2:
                    x=x-2
                if side==3:
                    y=y-2
                points.append(Point(x,y, z))

    return points


def renderRhinoFile(levels):
    f = open('generated/'+str(time.time())+'.py', 'w')
    fileWrite(f,"import rhinoscriptsyntax as rs")
    fileWrite(f, "rs.EnableRedraw(False)")
    fileWrite(f, "curves=[]")
    fileWrite(f, "strPath = rs.AddLine([0,0,0], [0,0,3])")

    y = 0
    for level in levels:
        pl = polygonRSformatter(level);
        fileWrite(f, "curve"+str(y)+" = rs.AddPolyline(["+pl+"])")
        # fileWrite(f, "rs.RebuildCurve ( curve"+str(y)+", degree=3, point_count=10)")
        fileWrite(f, "curves.append(curve"+str(y)+")")
        fileWrite(f, "rs.ExtrudeCurve(curve"+str(y)+", strPath)")
        y+=1
    
    fileWrite(f, "rs.EnableRedraw(True)")
    f.close()

def renderJsonFile(levels):
    data =[]
    for level in levels:
        pl = polygonRSformatter(level);
        data.append(pl)

    with open('generated/'+str(time.time())+'.json', 'w') as f:
        json.dump(data, f)
        f.close()

def polygonRSformatter(points):

    l = len(points)-1

    if points[0].x!= points[l].x or points[0].y!=points[l].y:
        points= np.append(points, points[0])
    ptsArr = []

    for point in points:
        ptsArr.append("(%s,%s,%s)"%(point.x,point.y,point.z))
    return ', '.join(ptsArr)
    
def fileWrite(f,txt):
    f.seek(0,2)
    f.write(txt+"\n\r")

def data2points(data, numLevels):
    points=[]
    numPoints = int(len(data)/2)
    pointsPerLevel = int(numPoints/numLevels)
    z=0
    for index in range(numPoints):
        if not index % pointsPerLevel:
            z=z+3
        points.append(Point(data[index*2], data[index*2+1],z))

    
    
    return np.array_split(np.array(points), numLevels)

def points2data(points):
    data=[]
    for point in points:
        data.append(point.x)
        data.append(point.y)
        # removing z value
    return data

def flattenPolygon(level):
    points = []

    for point in level:
        points.append(Point(point.x,point.y))
    
    return Polygon(points)

# Fitness functions
def getEvaluationMetrics(solution):
    building = data2points(solution, numLevels)
    data = []
    polygons = []

    # convert to polygons
    for level in building:
        polygons.append(flattenPolygon(level))

    # array of the floors, from the top
    floorStack = [polygons[len(polygons)-1]]

    #  run on all floors, beside the roof.
    for polygonsIndex in range(len(polygons)-1):
        current = len(polygons) - polygonsIndex-1

        balcony = polygons[polygonsIndex]

         # this calculates the polygon difference
        for currentBlaconyIndex in range(len(floorStack)):
            try:
                balcony = balcony.difference(floorStack[currentBlaconyIndex])

                if balcony.is_empty:
                    break;
            except:
                exce = 1

        floorStack.append(polygons[current])
    
    
        # Save balconies sizes and number
        if balcony.area>2:
            balconiesItems = get_parts(balcony).tolist()
            data.append({
                    'balconies': list(map(lambda x: x.area, balconiesItems)) ,
                    'number': len(balconiesItems),
                    'scopeArea': polygons[current].area / polygons[current].length
            })

    return data

# def calcLevelFitness(datum, p=False):
#     levelScore = []
#     # 4 balconies
#     if (datum['number'] ==4): levelScore.append(1)
#     else: levelScore.append(1/ abs(4-datum['number']))

#     # 2 sqrm
#     datum['balconies'].sort(reverse= True)
#     for balcon in range(len(datum['balconies'])):
#         if balcon > 4: break # no more than 4
#         # if (datum['balconies'][balcon] >= 2): levelScore.append(1)
#         # else: 
#         bal = datum['balconies'][balcon];
#         score = 10*bal+2-pow(bal,2)
#         if p: print(score)
#         levelScore.append(score)
    
#     levelScore.append(datum['scopeArea'])
#     print(levelScore)
#     return sum(levelScore)

def calcLevelFitness(datum, p=False):
    levelScore = []

    # 4 balconies
    # if (datum['number'] ==4): levelScore.append(1)
    # else: levelScore.append(1/ abs(4-datum['number']))

    # 2 sqrm
    datum['balconies'].sort(reverse= True)
    for balcon in range(len(datum['balconies'])):
        if balcon >= 4: break # no more than 4
        # if (datum['balconies'][balcon] >= 2): levelScore.append(1)
        # else: 
        bal = datum['balconies'][balcon];
        if (bal>2): score = 1
        else: score = 0
        # score = 10*bal+2-pow(bal,2)
        # if p: 
        # print(bal, score)
        levelScore.append(score)
    
    score = sum(levelScore) * datum['scopeArea']
    return score



# =================================================
# Initial settings
# =================================================

num_generations = 100
num_parents_mating = 50

# how many chromosomes (values) exist in each individual
parent_selection_type = "sss"
keep_parents = 1

crossover_type = "single_point"

mutation_type = "random"
mutation_percent_genes = 50
# random_mutation_min_val=-3
# random_mutation_max_val=3
numPoints = 36
numLevels = 30
initiaOptions = 100

thePlot = Polygon([(0,0), (35,0), (35,25), (0,35), (0,0)])

def main():
    
    def fitness_func(ga_instance, solution, solution_idx):
        data = getEvaluationMetrics(solution)
        score = []

        for datum in data:
            score.append(calcLevelFitness(datum))
        return sum(score)

    def on_gen(ga_instance):
        best = ga_instance.best_solution()
        print("Generation : ", ga_instance.generations_completed)
        print("Fitness of the best solution :", best[1])
        
        # data = getEvaluationMetrics(best[0])
        # print("======================")
        # for level in range(len(data)):
        #     score = calcLevelFitness(data[level])
        #     print("Level",level, data[level])
        #     print("Level score", score)
        # print("======================")


    # Holds the population
    data = []
    # generate several random creatures
    for i in range(initiaOptions):
        points = generateRandom(thePlot, numPoints, numLevels, 3)
        data.append(points2data(points))

    ga_instance = pygad.GA(
        initial_population=data,
        num_generations=num_generations,
        num_parents_mating=num_parents_mating,
        fitness_func=fitness_func,
        on_generation=on_gen,
        # sol_per_pop=sol_per_pop,
        # num_genes=num_genes,
        parallel_processing=8,
        # mutation_by_replacement=True,
        # random_mutation_min_val=random_mutation_min_val,
        # random_mutation_max_val=random_mutation_max_val,
        stop_criteria="saturate_10",
        gene_type=[float, 2],
        parent_selection_type=parent_selection_type,
        keep_parents=keep_parents,
        crossover_type=crossover_type,
        mutation_type=mutation_type,
        mutation_percent_genes=mutation_percent_genes)

    ga_instance.run()

    # ga_instance.plot_fitness(fontsize=10)

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(
        solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(
        solution_idx=solution_idx))
    
    renderJsonFile(data2points(solution, numLevels))
