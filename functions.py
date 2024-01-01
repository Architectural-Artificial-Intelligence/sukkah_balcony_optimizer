import pygad
import numpy as np
import statistics
import math
import time
import json
from shapely import Polygon, MultiPolygon, Point, get_num_geometries,get_coordinates, get_parts, geometry, unary_union, buffer, to_geojson, get_type_id


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

def generateInitialSolutions(howManyPoints, levels, levelOffset, scale):
    points = []
    for level in range(levels):
        z = levelOffset*level* scale
        sides = 4
        pointsInSide = int(howManyPoints/4)
        x = y = -howManyPoints/4/2* scale
        for side in range(sides):
            for current in range(pointsInSide):
                if side==0:
                    x=x+scale
                if side==1:
                    y=y+scale
                if side==2:
                    x=x-scale
                if side==3:
                    y=y-scale
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

    initiaOptions = 100
    numPoints = 36
    numLevels = 30
    
    # Set gen space
    gene_space = []

    #  Generate solutions
    data = []

    scale = 100
    # generate several random creatures
    for i in range(initiaOptions):
        points = generateInitialSolutions(numPoints, numLevels, 3, scale)
        data.append(geometryToData(points))
    


    min = geometryToData(generateInitialSolutions(numPoints, 1, 3, scale*0.8))
    max = geometryToData(generateInitialSolutions(numPoints, 1, 3, scale*1.4))

# dymanic bounding boxes for limits
    gene_space_level = []
    for i in range(len(min)):
        gene_space_level.append({"low":min[i],"high":max[i]})

#  for each level
    for i in range(numLevels):
        gene_space = gene_space + gene_space_level    
    
    def fitness_func(ga_instance, solution, solution_idx):

        # pts = generateInitialSolutions(numPoints,1,0)
        # block = dataToFlatGeomerty(pts,1)
        building = dataToFlatGeomerty(solution, numLevels)
        if (not len(building)):
            return 0
        optimalSize = pow(2*scale,2)
        score = []
        floorArea = []
        scope = []
        #  run on all floors, beside the roof.
        for floorndex in range(len(building)-1):

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
                    if (balconies[index]>0):
                        balScore = optimalSize-(abs(optimalSize - balconies[index]))
                        score.append(balScore)

        npScore = sum(score)
        # areaScore = 100 / abs(numLevels*numPoints*numPoints- statistics.mean(floorArea))
        # print(npScore, areaScore, npScore+ areaScore)
        return npScore # + areaScore #+ scopeScore 



    def on_gen(ga_instance):
        time_end = time.perf_counter()
        # calculate the duration
        
        time_duration = time_end - time_start
        # report the duration
        print(f'Took {time_duration:.3f} seconds')
        print("Generation : ", ga_instance.generations_completed)
        print("Fitness of the best solution :", ga_instance.best_solution()[1])

    filename = 'genetic2'

    ga_instance = pygad.GA(
        initial_population=data,
        num_generations=50,
        num_parents_mating=20,
        fitness_func=fitness_func,
        on_generation=on_gen,
        parallel_processing=8,
        
        stop_criteria="saturate_10",
        gene_type=int,
        gene_space=gene_space,
        # parent_selection_type="tournament",
        # keep_parents=  10,
        # crossover_type="uniform",
        mutation_type="random",
        # mutation_by_replacement=True,
        # mutation_percent_genes= 50,
        # random_mutation_min_val=-50,
        # random_mutation_max_val=50,
        # keep_elitism = 1
        # save_best_solutions=True,
        # allow_duplicate_genes=False
        )

    # ga_instance=  pygad.load(filename)
    # ga_instance.num_generations=1
    time_start = time.perf_counter()
    ga_instance.run()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(
        solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(
        solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(
        solution_idx=solution_idx))

    renderJsonFile(dataToGeomerty(solution, numLevels))
   
    ga_instance.save(filename=filename)

