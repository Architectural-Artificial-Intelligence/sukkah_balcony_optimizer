import time
import json
import pygad
import numpy as np
from shapely import Polygon, MultiPolygon, Point, get_parts, geometry, unary_union, buffer, to_geojson, get_type_id


def data_to_geomerty(data, num_levels):
    """Convert the gene data (string) to Shapely geometry by spliting to number of levels"""
    points = []
    num_points = int(len(data)/2)
    points_per_level = int(num_points/num_levels)
    z = 0
    for index in range(num_points):
        if not index % points_per_level:
            z = z+3
        points.append(Point(data[index*2], data[index*2+1], z))

    by_levels = np.array_split(np.array(points), num_levels)

    building = []
    for level in by_levels:
        building.append(buffer(Polygon(level),0))

    return building

def data_to_flat_geomerty(data, num_levels):
    """Convert the gene data (string) to Shapely geometry by spliting to number of levels, but without Z index """

    points = []
    num_points = int(len(data)/2)
    for index in range(num_points):
        points.append(Point(data[index*2], data[index*2+1]))

    by_levels = np.array_split(np.array(points), num_levels)

    building = []
    for level in by_levels:
        poly = buffer(Polygon(level),0)
        if (get_type_id(poly) != 3):
            return []
        
        building.append(poly.convex_hull)
    
    return building

def geometry_to_data(points):
    """Convery Point array to array"""
    data = []
    for point in points:
        data.append(point.x)
        data.append(point.y)
        # removing z value
    return data


def generate_initial_solutions(how_many_points, levels, level_offset, scale):
    """Takes building properties and produces an array of points, which is a square with multiple levels"""
    points = []
    for level in range(levels):
        z = level_offset*level* scale
        sides = 4
        points_in_side = int(how_many_points/4)
        x = y = -how_many_points/4/2* scale
        for side in range(sides):
            for current in range(points_in_side):
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


class NumpyEncoder(json.JSONEncoder):
    """Class that helps to conver geometric objects to JSON"""
    def default(self, o):
        if  isinstance(o, Polygon):
            return to_geojson(o)
        if  isinstance(o, MultiPolygon):
            return to_geojson(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, Point):
            return geometry.mapping(o)
        return json.JSONEncoder.default(self, o)


def write_json_file(levels,file_name):
    """Writes a building array as a JSON file"""
    data = []
    for level in levels:
        data.append(level)

    with open('generated/'+file_name+'.json', 'w') as f:
        json.dump(data, f, cls=NumpyEncoder)
        f.close()


# ============================
# Main
def main(filename):

    # Initial settings
    initia_options = 100
    num_points = 36
    num_levels = 30
    
    # Set gen space
    gene_space = []

    #  Generate solutions
    data = []

    scale = 100
    # generate initial buildings
    for i in range(initia_options):
        points = generate_initial_solutions(num_points, num_levels, 3, scale)
        data.append(geometry_to_data(points))
    

    # Define minimum and maximum range
    min_bounds = geometry_to_data(generate_initial_solutions(num_points, 1, 3, scale*0.8))
    max_bounds = geometry_to_data(generate_initial_solutions(num_points, 1, 3, scale*1.4))

# dymanic bounding boxes for limits
    gene_space_level = []
    for i in range(len(min_bounds)):
        gene_space_level.append({"low":min_bounds[i],"high":max_bounds[i]})

#  for each level
    for i in range(num_levels):
        gene_space = gene_space + gene_space_level    
    
    def fitness_func(ga_instance, solution, solution_idx):

        # pts = generate_initial_solutions(num_points,1,0)
        # block = data_to_flat_geomerty(pts,1)
        building = data_to_flat_geomerty(solution, num_levels)
        if (not len(building)):
            return 0
        optimal_size = pow(2*scale,2)
        score = []
        floor_area = []
        scope = []
        #  run on all floors, beside the roof.
        for floorndex in range(len(building)-1):

            #  current floor
            current_floor = building[floorndex]
            # Get roof
            try:
                roof = unary_union(building[floorndex::])
                # roof = unary_union(block, roof)
            except:
                print("unary_union failed with") 
                print(building[floorndex::])
                continue
            try:
                rest = current_floor.difference(roof)
                # rest = unary_union(block, rest)
            except:
                print("difference failed with") 
                print(current_floor, roof)
                continue

            if not current_floor.length:
                continue
            floor_area.append(current_floor.area - rest.area) 
            scope.append(current_floor.area / current_floor.length)

            all_balconies = get_parts(rest).tolist()
            # print(all_balconies)

            balconies = []
            for bal in all_balconies:
                balconies.append(bal.area)

            balconies = sorted(balconies, reverse= True)
            balconies = balconies[0:4:]

            if (balconies):
                for index in range(len(balconies)):
                    if (balconies[index]>0):
                        bal_score = optimal_size-(abs(optimal_size - balconies[index]))
                        score.append(bal_score)

        np_score = sum(score)
        return np_score 



    def on_gen(ga_instance):
        time_end = time.perf_counter()
        # calculate the duration
        
        time_duration = time_end - time_start
        # report the duration
        print(f'Took {time_duration:.3f} seconds')
        print("Generation : ", ga_instance.generations_completed)
        print("Fitness of the best solution :", ga_instance.best_solution()[1])

    # filename = 'genetic2'

    ga_instance = pygad.GA(
        initial_population=data,
        num_generations=100,
        num_parents_mating=20,
        fitness_func=fitness_func,
        on_generation=on_gen,
        parallel_processing=8,
        
        stop_criteria="saturate_20",
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
        keep_elitism = 1
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

    write_json_file(data_to_geomerty(solution, num_levels), filename)
   
    ga_instance.save(filename=filename)

