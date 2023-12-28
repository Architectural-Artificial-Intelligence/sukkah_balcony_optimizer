import pygad
import numpy as np
import statistics
import math
import time
import json
from shapely import Polygon, MultiPolygon, Point, get_num_geometries, get_parts, geometry, unary_union, buffer, to_geojson, get_type_id


# ============================
# Data encoders

def dataToGeomerty(data, numLevels):
    points = []
    numPoints = int(len(data)/2)
    pointsPerLevel = int(numPoints/numLevels)
    z = 0
    for index in range(numPoints):
        if not index % pointsPerLevel:
            z = z+3
        points.append(Point(data[index*2], data[index*2+1], z))

    byLevels = np.array_split(np.array(points), numLevels)

    building = []
    for level in byLevels:
        building.append(buffer(Polygon(level),0))
    
    return building;

def dataToFlatGeomerty(data, numLevels):
    points = []
    numPoints = int(len(data)/2)
    pointsPerLevel = int(numPoints/numLevels)
    for index in range(numPoints):
        points.append(Point(data[index*2], data[index*2+1]))

    byLevels = np.array_split(np.array(points), numLevels)

    building = []
    for level in byLevels:
        poly = buffer(Polygon(level),0)
        if (get_type_id(poly) != 3):
            return []
        
        building.append(poly.convex_hull)
    
    return building;

def geometryToData(points):
    data = []
    for point in points:
        data.append(point.x)
        data.append(point.y)
        # removing z value
    return data

# ============================
# Geometric functions

def generateInitialSolutions(howManyPoints, levels, levelOffset):
    points = []
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

def getArea(elm):
    return elm.area

# ============================
# File functions


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if  isinstance(obj, Polygon):
            return to_geojson(obj)
        if  isinstance(obj, MultiPolygon):
            return to_geojson(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, Point):
            return geometry.mapping(obj)
        return json.JSONEncoder.default(self, obj)


def renderJsonFile(levels):
    data = []
    for level in levels:
        # pl = polygonRSformatter(level);
        data.append(level)

    with open('generated/'+str(time.time())+'.json', 'w') as f:
        json.dump(data, f, cls=NumpyEncoder)
        f.close()


# ============================
# Main
def main():

    # =================================================
    # Initial settings
    # =================================================

    num_generations = 200
    initiaOptions = 50
    num_parents_mating = 25

    # how many chromosomes (values) exist in each individual
    parent_selection_type = "sss"
    keep_parents = 1

    crossover_type = "single_point"

    # mutation_type = "random"
    # mutation_percent_genes = 10
    mutation_type="adaptive"
    mutation_percent_genes = [25, 12]
    
    random_mutation_min_val = -0.1
    random_mutation_max_val = 1
    numPoints = 20
    numLevels = 30
    

    # Generate optimum building
    optimum = np.full((numLevels-1,4), 4, dtype=float)

    #  Generate solutions
    data = []

    # generate several random creatures
    for i in range(initiaOptions):
        points = generateInitialSolutions(numPoints, numLevels, 3)
        data.append(geometryToData(points))


    
    def fitness_func(ga_instance, solution, solution_idx):

        # pts = generateInitialSolutions(numPoints,1,0)
        # block = dataToFlatGeomerty(pts,1)
        building = dataToFlatGeomerty(solution, numLevels)
        if (not len(building)):
            return 0
        score = []
        floorArea = []
        scope = []
        #  run on all floors, beside the roof.
        for floorndex in range(len(building)-1):

            score.append([0,0,0,0])

            #  current floor
            currentFloor = building[floorndex]
            # Get roof
            try:
                roof = unary_union(building[floorndex::])
                # roof = unary_union(block, roof)
            except:
                print("unary_union failed with") 
                print(building[floorndex::])
                continue;
            try:
                rest = currentFloor.difference(roof)
                # rest = unary_union(block, rest)
            except:
                print("difference failed with") 
                print(currentFloor, roof)
                continue;
            
            if not currentFloor.length:
                continue;
            floorArea.append(currentFloor.area - rest.area) 
            scope.append(currentFloor.area / currentFloor.length)

            allBalconies = get_parts(rest).tolist()
            # print(allBalconies)
            
            balconies = []
            for bal in allBalconies:
                balconies.append(bal.area)

            balconies = sorted(balconies, reverse= True)
            balconies = balconies[0:4:]

            # print(len(building[floorndex::]),len(building), roof.area, rest.area, len(allBalconies) )
            # print(balconies)
            
            if (balconies):
                # print(balconies);
                for index in range(len(balconies)):
                    score[floorndex][index]=balconies[index]
        
       
        # npScore = 1.0000000/ np.abs(np.array(score, dtype='f')- optimum)

        # Size of balconies
        npScore = 16/ abs(16-np.sum(np.array(score, dtype='f')))
        # print(npScore)
        # Distance to optimal area
        areaScore = 100 / abs(numLevels*numPoints*numPoints- statistics.mean(floorArea))
        # Degree of scope
        # scopeScore = 10/ abs(40.00001 - sum(floorArea) / sum(scope)) 
        # print(npScore , areaScore )
            #   , scopeScore)
        return npScore + areaScore #+ scopeScore 



    def on_gen(ga_instance):
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        # print(f"Parameters of the best solution : {solution}")
        print(f"Fitness value of the best solution = {solution_fitness}")
        # print(f"Index of the best solution : {solution_idx}")


    ga_instance = pygad.GA(
        initial_population=data,
        num_generations=num_generations,
        num_parents_mating=num_parents_mating,
        fitness_func=fitness_func,
        on_generation=on_gen,
        parallel_processing=8,
        random_mutation_min_val=random_mutation_min_val,
        random_mutation_max_val=random_mutation_max_val,
        # stop_criteria="saturate_10",
        gene_type=[float,2],
        parent_selection_type=parent_selection_type,
        keep_parents=keep_parents,
        crossover_type=crossover_type,
        mutation_type=mutation_type,
        mutation_percent_genes=mutation_percent_genes)

    ga_instance.run()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(
        solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(
        solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(
        solution_idx=solution_idx))

    renderJsonFile(dataToGeomerty(solution, numLevels))


