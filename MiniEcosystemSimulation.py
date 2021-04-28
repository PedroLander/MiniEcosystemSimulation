import sys
import numpy as np
import random
# import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# import multiprocessing
# import threading

"""
Parameters

These are like nobs that you can turn and tweak to effect how the simulation runs
"""

# World Parameters
x = 98
y = 98
initial_world_resources = "1,000,000"
initial_resources_generated = .8
# Population Parameters
sheep_p = 0.01
wolfe_p = 0.01
fitness_depletion = 0.02
movement_energy_perc_loss = 0.001
threshold_energy = 1
threshold_fitness = 1
sd_multiplier = 15 / 100
# Wolfe Parameters
wolfe_genes_dict = {
    "mean fitness": 100,
    "sd fitness"  : 100 * sd_multiplier,
    "mean energy" : 100,
    "sd energy"   : 15,
    "speed"       : 1
}
# Sheep Parameters
sheep_genes_dict = {
    "mean fitness": 75,
    "sd fitness"  : 75 * sd_multiplier,
    "mean energy" : 50,
    "sd energy"   : 7.5,
    "speed"       : 1
}
# Grass Parameters
grass_genes_dict = {
    "mean nutrients": 3,
    "sd nutrients"  : 3 * sd_multiplier
}
# Shrub Parameters
shrub_genes_dict = {
    "mean nutrients": 7,
    "sd nutrients"  : 7 * sd_multiplier
}
# Children Parameters
required_parents_num = 2
energy_perc_for_child = 0.2
perc_of_characteristics_given = 0.6
# Predator Parameters
predator_list = ["Wolfe"]
energy_used_attacking = .05  # 0.3
fitness_used_attacking = .001  # 0.3
# Prey Parameters
prey_list = ["Sheep", "Wolfe"]
herbivore_list = ["Sheep"]
energy_defending = 0.5
fitness_defending = 0.5
# Food Parameters
prob_rand_food_gen = 0.001
rand_min_food_nutrients = 2
rand_max_food_nutrients = 5
hunt_eat_keep = 0.7
veg_eat_keep = 0.01
# Time Parameters
hours_per_day = 24
days_per_year = 356
# Mass Placement Parameters
mass_placement_size = 15
creature_placement_deviation = 15
mass_min_food_nutrients = 100
mass_max_food_nutrients = 200
# Color Parameters
DRAKONIAN_ON = 20
GRITIS_ON = 255
GRASS_ON = 120
SHRUB_ON = 100
FIGHT_ON = 20
OFF = 200

"""
Setters

These are the initializer variables
"""

# General World Setters
initial_world_resources = int(initial_world_resources.replace(",", ""))
world_resources = initial_world_resources
population = dict()
food_pot = dict()
p_off = 1 - wolfe_p - sheep_p
vals = [DRAKONIAN_ON, GRITIS_ON, OFF]
animal_list = ["Sheep", "Wolfe"]
plant_list = ["grass", "shrub"]
species_genes_dict = {
    "Animal": {
        "Sheep"   : sheep_genes_dict,
        "Wolfe": wolfe_genes_dict
        },
    "Plant" : {
        "grass": grass_genes_dict,
        "shrub": shrub_genes_dict
        }
}
animal_color_dict = {"Sheep": GRITIS_ON, "Wolfe": DRAKONIAN_ON}
plant_color_dict = {"grass": GRASS_ON, "shrub": SHRUB_ON}
color_species_dict = {value: key for key, value in animal_color_dict.items()}
color_plant_dict = {value: key for key, value in plant_color_dict.items()}
new_grid = np.array([])
required_parents_num -= 1
max_energy = 0
max_age = 0
death_count = 0
# Wolfe Setters
wolfe_pop_size = 0
max_darkonian_age = 0
avg_wolfe_fitness = 0
avg_wolfe_energy = 0
# Sheep Setters
sheep_pop_size = 0
max_sheep_age = 0
avg_sheep_fitness = 0
avg_sheep_energy = 0
# Day Setters
year = 0
day = 0
old_day = day
hour = 0
# User Interaction Setters
ix = -1
iy = -1
mouse_side = "None"
pause = False
bomb_set = False
thanos_on = False
mass_food = False
mass_sheep_placement = False
mass_wolfe_placement = False
single_creature_display = False
indiv_fitness = 0
indiv_energy = 0
indiv_age = 0


# Extra
# DRAKONIAN_ON = 60
# GRITIS_ON = 255
# FOOD_ON = 200
# Number of Threads
# processes_count = 2
# threads_count = 2


class UserActions:
    @staticmethod
    def onclick(event):
        global food_pot
        global ix, iy
        global mouse_side

        if str(event.button) == "MouseButton.LEFT":
            mouse_side = "Left"

            species = random.choice(plant_list)
            genes = species_genes_dict["Plant"][species]

            ix, iy = int(event.xdata), int(event.ydata)
            # print('x = %d, y = %d' % (ix, iy))

            food_pot[iy, ix] = np.random.normal(genes["a nutrients"], genes["sd nutrients"])

        elif str(event.button) == "MouseButton.RIGHT":
            mouse_side = "Right"
            ix, iy = int(event.xdata), int(event.ydata)

    # print('x = %d, y = %d' % (ix, iy))

    @staticmethod
    def key_event(event):
        global pause
        global bomb_set
        global thanos_on
        global mass_food
        global mass_sheep_placement
        global mass_wolfe_placement
        global world_resources

        # ctrl+p for something different
        if str(event.key) == "p":
            pause = not pause

        elif str(event.key) == "b":
            bomb_set = not bomb_set

        elif str(event.key) == "t":
            thanos_on = True

        elif str(event.key) == "m":
            mass_food = not mass_food
            mass_sheep_placement = False
            mass_wolfe_placement = False

        elif str(event.key) == "1":
            mass_sheep_placement = not mass_sheep_placement
            mass_food = False
            mass_wolfe_placement = False

        elif str(event.key) == "2":
            mass_wolfe_placement = not mass_wolfe_placement
            mass_food = False
            mass_sheep_placement = False

        elif str(event.key) == "w":
            world_resources += initial_world_resources

        elif str(event.key) == "q":
            sys.exit()

    def update(self):
        global world_resources
        global mouse_side
        global thanos_on
        global food_pot
        global ix, iy

        if thanos_on:
            keys = []
            for key in population:
                keys.append(key)

            for pos in range(0, len(keys), 2):
                del population[keys[pos]]
                new_grid[keys[pos]] = OFF

            thanos_on = False

        if mouse_side == "Left":
            if bomb_set:
                for row in range(-mass_placement_size, mass_placement_size):
                    for col in range(-mass_placement_size, mass_placement_size):
                        pos = (iy + col, ix + row)
                        if pos in population:
                            del population[pos]
                            new_grid[pos] = OFF
                        if pos in food_pot:
                            del food_pot[pos]
                            new_grid[pos] = OFF

            if mass_food:
                for row in range(-mass_placement_size, mass_placement_size + 1):
                    for col in range(-mass_placement_size, mass_placement_size + 1):
                        generate.generate_resource((iy + col) % x, (ix + row) % y, world_resources)

            if mass_wolfe_placement or mass_sheep_placement:
                for row in range(-mass_placement_size, mass_placement_size + 1):
                    for col in range(-mass_placement_size, mass_placement_size + 1):
                        # Get the species the user wants to place
                        species = "Wolfe"
                        if mass_wolfe_placement:
                            species = "Wolfe"
                        elif mass_sheep_placement:
                            species = "Sheep"
                        pos = ((iy + col) % x, (ix + row) % y)

                        if pos not in population:
                            genes = species_genes_dict["Animal"][species]
                            generate.generate_creature(
                                species,
                                pos,
                                mean_fitness=genes["mean fitness"],
                                sd_fitness=genes["sd fitness"],
                                mean_energy=genes["mean energy"],
                                sd_energy=genes["sd energy"],
                                speed=genes["speed"]
                            )
                            new_grid[pos] = animal_color_dict[species]

            # if we did not just start the program, hence ix and iy would be -1 if we did
            # then add the food_pot to the new grid
            if not mass_food and not bomb_set and not mass_sheep_placement and not mass_wolfe_placement:
                new_grid[(iy, ix)] = FOOD_ON

            ix, iy = -1, -1

        elif mouse_side == "Right":
            global single_creature_display
            global indiv_fitness
            global indiv_energy
            global indiv_age

            single_creature_display = not single_creature_display
            if single_creature_display and (iy, ix) in population:
                selected_creature_id = (iy, ix)
                creature = population[selected_creature_id]
                indiv_fitness = creature["fitness"]
                indiv_energy = creature["energy"]
                indiv_age = creature["age"]

        mouse_side = "None"


class Generate:
    def generate_world(self, world_resources):
        random_grid = self.generate_population()
        random_grid, world_resources = self.generate_terrain(random_grid, world_resources)
        return random_grid, world_resources

    def generate_population(self):
        random_grid = np.random.choice(
            vals, x * y, p=[wolfe_p, sheep_p, p_off]).reshape(x, y)
        for i in range(y):
            for j in range(x):
                key = (j, i)
                if random_grid[key] in color_species_dict:
                    species = color_species_dict[random_grid[key]]
                    genes = species_genes_dict["Animal"][species]
                    self.generate_creature(
                        species,
                        key,
                        mean_fitness=genes["mean fitness"],
                        sd_fitness=genes["sd fitness"],
                        mean_energy=genes["mean energy"],
                        sd_energy=genes["sd energy"],
                        speed=genes["speed"]
                    )
        return random_grid

    def generate_terrain(self, random_grid, world_resources):
        for i in range(y):
            for j in range(x):
                if random.random() <= initial_resources_generated and (j, i) not in population:
                    plant_type = random.choice(plant_list)
                    genes = species_genes_dict["Plant"][plant_type]
                    plant = dict()
                    plant["species"] = plant_type
                    plant["nutrients"] = np.random.normal(genes["mean nutrients"], genes["sd nutrients"])
                    food_pot[(j, i)] = plant
                    random_grid[j, i] = plant_color_dict[plant_type]
                    world_resources -= 1
        return random_grid, world_resources

    @staticmethod
    def generate_creature(species, key, mean_fitness, sd_fitness, mean_energy, sd_energy, speed):
        characteristics = dict()
        # species
        characteristics["species"] = species
        # add fitness
        characteristics["fitness"] = np.random.normal(mean_fitness, sd_fitness)
        # add energy
        characteristics["energy"] = np.random.normal(mean_energy, sd_energy)
        print(species, characteristics["fitness"], characteristics["energy"])
        # add energy
        characteristics["speed"] = speed
        # add reproduction probability for number of kids creature has
        characteristics["age"] = 0

        population[key] = characteristics

    @staticmethod
    def generate_resource(j, i, world_resources):
        plant_type = random.choice(plant_list)
        genes = species_genes_dict["Plant"][plant_type]
        plant = dict()
        plant["species"] = plant_type
        plant["nutrients"] = np.random.normal(genes["mean nutrients"], genes["sd nutrients"])
        food_pot[(j, i)] = plant
        new_grid[j, i] = plant_color_dict[plant_type]
        world_resources -= 1

        return world_resources

    def rand_generate_food(self, world_resources, grid):
        for j in range(x):
            for j in range(y):
                if world_resources > 0:
                    i = random.randint(0, y - 1)
                    j = random.randint(0, x - 1)
                    if grid[j, i] == OFF:
                        if random.random() <= prob_rand_food_gen:
                            world_resources = self.generate_resource(j, i, world_resources)
                else:
                    break
        return world_resources


class CreatureActions:
    def __init__(self):
        self.generate = Generate()

    @staticmethod
    def creature_consume_food():
        global new_grid

        # copy food keys so we can edit the dictionary
        keys = []
        amount_of_food = 0
        for key in food_pot:
            keys.append(key)
            amount_of_food += 1

        # if the size of the population is smaller than the amount of existing food, then check each creature with
        # each food to see if they are touching. This makes it faster that checking every food with every creatrue
        # if not, then run the else
        if sheep_pop_size + wolfe_pop_size < amount_of_food:
            # check all of the creatures to see if they reached food
            for food_loc in keys:
                can_eat_veg = population[food_loc]["species"] in herbivore_list if food_loc in population else False
                if can_eat_veg:
                    creature = population[food_loc]
                    creature["fitness"] += food_pot[food_loc]["nutrients"] * veg_eat_keep
                    creature["energy"] += food_pot[food_loc]["nutrients"] * veg_eat_keep
                    del food_pot[food_loc]
                    # since the creature is at the food location, simply turn it from food on to just on for the
                    # creature to now be displayed instead of the food
                    new_grid[food_loc] = animal_color_dict[population[food_loc]["species"]]

        else:
            # check all of the creatures to see if they reached food
            for creature_loc in population:
                can_eat_veg = population[creature_loc][
                                  "species"] in herbivore_list if creature_loc in population else False
                if can_eat_veg and creature_loc in food_pot:
                    creature = population[creature_loc]
                    creature["fitness"] += food_pot[creature_loc]["nutrients"] * veg_eat_keep
                    creature["energy"] += food_pot[creature_loc]["nutrients"] * veg_eat_keep
                    del food_pot[creature_loc]
                    # since the creature is at the food location, simply turn it from food on to just on for the
                    # creature to now be displayed instead of the food
                    new_grid[creature_loc] = animal_color_dict[population[creature_loc]["species"]]

    @staticmethod
    def reproduce(grid, keys):
        for key in keys:
            creature = population[key]

            # update every creatures age by 1
            # we do not create a separate function to loop through all creatures for small stuff like this
            # as that would add a lot of unneeded processing time. Thus we trade readability for complexity time
            # print(day, old_day)
            # assert day - old_day < 2
            # if day != old_day:
            #     # print(original_creature)
            #     creature["age"] = creature["age"] + 1
            #     # print("ran", key, original_creature["age"])

            # this grabs the color for the species that the creature is
            ON = animal_color_dict[creature["species"]]

            # try:
            #     if grid[key] == ON:
            #         print(key)
            # except:
            #     print()
            #     print()
            #     print(key)
            # only do the rest if there is actually a creature that is there
            if grid[key] == ON:

                # we use i and j specifically for moving the creature to a new grid location/create new id
                j = key[0]
                i = key[1]

                # compute 8-neighbor sum
                # using toroidal boundary conditions - x and y wrap around
                # so that the simulation takes place on a toroidal surface.
                possible_parents = []
                total = 0
                if grid[j, (i - 1) % y] == ON:
                    possible_parents.append((j, (i - 1) % y))
                    total += 1
                if grid[j, (i + 1) % y] == ON:
                    possible_parents.append((j, (i + 1) % y))
                    total += 1
                if grid[(j - 1) % x, i] == ON:
                    possible_parents.append(((j - 1) % x, i))
                    total += 1
                if grid[(j + 1) % x, i] == ON:
                    possible_parents.append(((j + 1) % x, i))
                    total += 1
                if grid[(j - 1) % x, (i - 1) % y] == ON:
                    possible_parents.append(((j - 1) % x, (i - 1) % y))
                    total += 1
                if grid[(j - 1) % x, (i + 1) % y] == ON:
                    possible_parents.append(((j - 1) % x, (i + 1) % y))
                    total += 1
                if grid[(j + 1) % x, (i - 1) % y] == ON:
                    possible_parents.append(((j + 1) % x, (i - 1) % y))
                    total += 1
                if grid[(j + 1) % x, (i + 1) % y] == ON:
                    possible_parents.append(((j + 1) % x, (i + 1) % y))
                    total += 1

                # create new creatures randomly next to the parent1 if there is the needed number of parent1s and
                # the energy is higher proportionally compared to the fitness of the creature at j, i
                # if the world is filling up to fast change the total == to a higher number so there must be a greater
                # of other creatures next to the creature for it to procreate
                if total >= required_parents_num and creature["energy"] > creature["fitness"] * energy_perc_for_child:
                    new_id = 0
                    r = random.randint(0, 7)
                    if r == 0:
                        new_id = (j, (i - 1) % y)
                    if r == 1:
                        new_id = (j, (i + 1) % y)
                    if r == 2:
                        new_id = ((j - 1) % x, i)
                    if r == 3:
                        new_id = ((j + 1) % x, i)
                    if r == 4:
                        new_id = ((j - 1) % x, (i - 1) % y)
                    if r == 5:
                        new_id = ((j - 1) % x, (i + 1) % y)
                    if r == 6:
                        new_id = ((j + 1) % x, (i - 1) % y)
                    if r == 7:
                        new_id = ((j + 1) % x, (i + 1) % y)

                    parents = list()
                    parents_keys = list()
                    for count in range(required_parents_num):
                        # need parent index to delete creature later
                        parent_index = random.randint(0, len(possible_parents) - 1)
                        parent_key = possible_parents[parent_index]
                        parents_keys.append(parent_key)
                        parents.append(population[parent_key])
                        del possible_parents[parent_index]

                    combined_fitness = sum([parent["fitness"] for parent in parents])
                    # give the average of the parents fitness to the child
                    fitness_given = combined_fitness // len(parents)
                    combined_energy = sum([parent["energy"] for parent in parents])
                    # give the average of the parents energy to the child
                    energy_given = combined_energy // len(parents)

                    # create the child first and add some of the parents fitness/energy
                    parents_species = [parent["species"] for parent in parents]
                    child = dict()
                    child["species"] = max(set(parents_species), key=parents_species.count)
                    child["fitness"] = fitness_given
                    child["energy"] = energy_given
                    child["age"] = 0

                    # remove fitness from parent1 and parent2 even if child does not make it
                    for parent_index in range(len(parents)):
                        parents[parent_index]["fitness"] -= (fitness_given * perc_of_characteristics_given)
                        parents[parent_index]["energy"] -= (energy_given * perc_of_characteristics_given)

                    for key, parent in zip(parents_keys, parents):
                        population[key] = parent
                    if new_id in population:
                        # get creature at new_id as that's the position the child will go to
                        other = population[new_id]
                        if child["fitness"] > other["fitness"]:
                            # keep the key as the key does not change, but change the creature as that does
                            population[new_id] = child
                        # else, if other fitness is greater than child fitness than do nothing as other stays there and
                        # child dies, hence not added to board but is added to death count
                    else:
                        # if there is not another creature there add the child to the population and to the new grid
                        population[new_id] = child
                        new_grid[new_id] = ON

    # def move_all_creatures(self, keys, hour):
    #     print(population)
    #     keys_length = len(keys)
    #     partition_size = keys_length // processes_count
    #     partitions_list = [count * partition_size for count in range(processes_count)]
    #     # separate this because there if not there will be extra creatures not visited
    #     partitions_list.append(keys_length)
    #
    #     jobs = []
    #     for index in range(processes_count):
    #         partition_start = partitions_list[index]
    #         partition_end = partitions_list[index + 1]
    #         process = multiprocessing.Process(target=self.creature_movement, args=(keys[partition_start: partition_end], hour,))
    #         jobs.append(process)
    #         process.start()
    #
    #     for process in jobs:
    #         process.terminate()
    #         process.join()

    # def move_all_creatures(self, keys, hour):
    #     keys_length = len(keys)
    #     partition_size = keys_length // threads_count
    #     partitions_list = [count * partition_size for count in range(threads_count)]
    #     # separate this because there if not there will be extra creatures not visited
    #     partitions_list.append(keys_length)
    #
    #     jobs = []
    #     for index in range(threads_count):
    #         partition_start = partitions_list[index]
    #         partition_end = partitions_list[index + 1]
    #         process = threading.Thread(target=self.creature_movement, args=(keys[partition_start: partition_end], hour,))
    #         jobs.append(process)
    #         process.start()
    #
    #     for process in jobs:
    #         process.join()

    @staticmethod
    # def creature_movement(keys, hour):
    def move_all_creatures(ids, hour):
        for id in ids:
            original_creature = population[id]
            genes = species_genes_dict["Animal"][original_creature["species"]]

            # since we start with an even time and end with an even time, and since the time loops, we may run into a
            # a problem here, so fix this bug

            # nevertheless, we are checking if the hour is even, if so every creature gets to move, if not
            # then check if the creature is wolfe, if they are then they always get to move, regardless of the time
            # aka, they wolfes move every hour, while the rest move every other hour
            if hour % genes["speed"] == 0:
                # Subtract the energy loss from movement once the creature moves. If they are Wolfe, this happen more
                # often, but they also get to move more often
                # print(original_creature["energy"])
                original_creature["energy"] -= original_creature["energy"] * movement_energy_perc_loss
                # print(original_creature["energy"])
                # print()

                j = id[0]
                i = id[1]
                possible_spots = [(j, (i - 1) % y), (j, (i + 1) % y), ((j - 1) % x, i), (
                    (j + 1) % x, i), ((j - 1) % x, (i - 1) % y), ((j - 1) % x, (i + 1) % y),
                                  ((j + 1) % x, (i - 1) % y), ((j + 1) % x, (i + 1) % y)]
                new_id = random.choice(possible_spots)

                is_predator = original_creature["species"] in predator_list
                # check if there is even a creature in new spot, if not then set both to false
                is_prey = population[new_id][
                              "species"] in prey_list if new_id in population else False

                # if eat
                # could possibly add neural net that determines if eat eats its own kind
                if is_predator and is_prey:
                    predator_id = id
                    prey_id = new_id
                    predator = original_creature
                    prey = population[prey_id]

                    # subtract some energy from the predator as it used to attack
                    predator["energy"] *= energy_used_attacking
                    predator["fitness"] -= prey["fitness"] * fitness_used_attacking
                    # subtract some energy from the prey for fighting back/fleeing
                    prey["energy"] *= energy_defending
                    prey["fitness"] -= predator["fitness"] * fitness_defending

                    # First check predator state
                    # prey kills predator
                    # if dead
                    if predator["fitness"] <= 0:
                        # turn position of predator off since it died
                        new_grid[predator_id] = OFF if id not in food_pot else animal_color_dict[population[predator_id]["species"]]
                        # remove it from the population
                        del population[predator_id]
                    else:
                        # otherwise, keep the predator in the same position just update it and keep that position on
                        # if alive
                        population[predator_id] = predator

                    # Next check preys state
                    # if predator is still alive and predator kills prey and
                    # if dead
                    if predator_id in population and prey["fitness"] <= 0:
                        # if the challenger is fitter than the creature currently at the position
                        # then set the final alive creature to the challenger
                        predator["fitness"] += prey["fitness"] * hunt_eat_keep
                        predator["energy"] += predator["energy"] * hunt_eat_keep

                        # delete creature at old position as it has now taken the spot of the prey
                        del population[predator_id]
                        # turn off the old spot if that spot did not have food origianlly there
                        # if it did, then turn it back to that original color
                        new_grid[predator_id] = OFF if predator_id not in food_pot else plant_color_dict[food_pot[predator_id]["species"]]

                        # make the prey id that used to be there the predator
                        population[prey_id] = predator
                        # set the new spot to the color of the predator
                        new_grid[prey_id] = animal_color_dict[predator["species"]]
                    else:
                        # if alive
                        # otherwise update the preys state
                        population[prey_id] = prey

                # if there is not prey there and/or food
                else:
                    # get rid of old creature as old creature doesnt exist there anymore
                    del population[id]
                    # turn off the old spot
                    new_grid[id] = OFF
                    # move the creature to new spot
                    population[new_id] = original_creature
                    # change the color to that of the creature as the creature will walk over the new spot
                    new_grid[new_id] = animal_color_dict[original_creature["species"]]
                # dont change anything else as the creature is simply standing there

                # finally, check if the old spot id is in the food_pot dictionary because if so that means that the food
                # was never eaten. Because if it was then the food would no longer exist there, but it does, so that
                # means the food was simply walked over and now we must change that old spot on the grid to back to the
                # color of food
                if id in food_pot:
                    new_grid[id] = plant_color_dict[food_pot[id]["species"]]

    @staticmethod
    def check_heart_beat():
        ids = population.copy()
        for id in ids:
            creature = population[id]
            # if the creature doesnt have energy than deplete its fitness some
            if creature["energy"] <= threshold_energy:
                creature["fitness"] -= creature["fitness"] * fitness_depletion
                population[id] = creature

            # if the creature doesnt have fitness kill it
            if creature["fitness"] <= threshold_fitness:
                del population[id]
                new_grid[id] = OFF if id not in food_pot else plant_color_dict[food_pot[id]["species"]]

    def update(self, grid):
        global hour
        global day
        global year
        global new_grid
        global max_energy
        global max_age
        global world_resources

        # copy the keys so we can edit the population dictionaries. We do it this way so that we can also find the
        # max fitness and energy
        population_keys = utils.stats()

        world_resources = self.generate.rand_generate_food(world_resources, grid)

        self.creature_consume_food()

        # this first loop is for the creatures to have children first
        self.reproduce(grid, population_keys)

        # then this second loop is to have the creatures and the kids to move about the world
        self.move_all_creatures(population_keys, hour)

        # hour completed, so add to hour count
        hour, day, old_day, year = utils.update_time(hour, day, year)

        self.check_heart_beat()


class Utils:
    def __init__(self):
        self.creature_action = CreatureActions()
        self.user_action = UserActions()

    @staticmethod
    def update_time(hour, day, year):
        hour += 1
        old_day = day
        if hour % hours_per_day == 0:
            day += 1
            hour = 0
        if day != 0 and day % days_per_year == 0:
            year += 1
            day = 0

        return hour, day, old_day, year

    @staticmethod
    def stats():
        global wolfe_pop_size
        global sheep_pop_size
        global avg_wolfe_fitness
        global avg_sheep_fitness
        global avg_wolfe_energy
        global avg_sheep_energy

        # copy keys and get stats
        keys = []
        wolfe_pop_size = 0
        sheep_pop_size = 0
        total_wolfe_fitness = 0
        total_sheep_fitness = 0
        total_wolfe_energy = 0
        total_sheep_energy = 0
        for key in population:
            creature = population[key]

            # determine if sheep or wolfe and add to their population
            # size, and in the same breath, calculate average fitness
            # and average energy for that species
            if creature["species"] == "Wolfe":
                wolfe_pop_size += 1
                total_wolfe_fitness += creature["fitness"]
                total_wolfe_energy += creature["energy"]

            if creature["species"] == "Sheep":
                sheep_pop_size += 1
                total_sheep_fitness += creature["fitness"]
                total_sheep_energy += creature["energy"]

            # if creature["energy"] > max_energy:
            #     max_energy = creature["energy"]
            # if creature["age"] > max_age:
            #     max_age = creature["age"]

            keys.append(key)

        # take averages because we do not need a lot of precision
        if wolfe_pop_size != 0:
            avg_wolfe_fitness = round(total_wolfe_fitness / wolfe_pop_size, 3)
            avg_wolfe_energy = round(total_wolfe_energy / wolfe_pop_size, 3)
        else:
            avg_wolfe_fitness = 0
            avg_wolfe_energy = 0

        if sheep_pop_size != 0:
            avg_sheep_fitness = round(total_sheep_fitness / sheep_pop_size, 3)
            avg_sheep_energy = round(total_sheep_energy / sheep_pop_size, 3)
        else:
            avg_sheep_fitness = 0
            avg_sheep_energy = 0

        return keys

    @staticmethod
    def display_info(img, past_pop_size):
        global death_count

        diff = past_pop_size - len(population)
        death_count += diff if diff > 0 else 0

        plt.title(
            f"Y:D:H: {year}:{day}:{hour} - Alive: {wolfe_pop_size + sheep_pop_size:,} - Death Count: {death_count:,}",
            fontsize=14)
        plt.suptitle(f"World Resources: {world_resources:,}"
                     f"\nN: D:{wolfe_pop_size:,} G: {sheep_pop_size:,}"
                     f"\nAvg D-F: {avg_wolfe_fitness:,.1f} G-F: {avg_sheep_fitness:,.1f}"
                     f"\nAvg: D-E: {avg_wolfe_energy:,.1f} G-E: {avg_sheep_energy:,.1f}", fontsize=11)

        # print(random.choice(list(population.items())))

        # if single_creature_display:
        # 	plt.xlabel(
        # 		f"CreatureActions {selected_creature_id} Fitness: {indiv_fitness}",
        # 		fontsize=11)
        img.set_data(new_grid)


def update(frameNum, fig, img, grid):
    global new_grid

    # time.sleep(0.1)

    # indiv_fitness = 0
    # selected_creature_id = (-1, -1)

    pop_size = len(population)

    new_grid = grid.copy()

    creature_actions.update(grid) if not pause else None

    fig.canvas.mpl_connect('button_press_event', user_actions.onclick)
    fig.canvas.mpl_connect('key_press_event', user_actions.key_event)
    user_actions.update()

    # utils.display_info(img, indiv_fitness, selected_creature_id)
    utils.display_info(img, pop_size)
    grid[:] = new_grid[:]

    return img,


creature_actions = CreatureActions()
user_actions = UserActions()
utils = Utils()
generate = Generate()


def main():
    global world_resources

    # declare grid
    generate = Generate()
    grid, world_resources = generate.generate_world(world_resources)

    # set up animation
    # set animation update interval
    updateInterval = 1
    fig, ax = plt.subplots(constrained_layout=True)
    fig.canvas.manager.full_screen_toggle()
    img = ax.imshow(grid, cmap="terrain")

    # show animation
    count = 0
    while True:
        # show animation
        ani = animation.FuncAnimation(
            fig,
            update,
            fargs=(fig, img, grid,),
            frames=10,
            interval=updateInterval,
            save_count=50)

        plt.axis('off')
        plt.show()

        # input()

        if count == 100:
            # console.clear()
            count = 0

        count += 1


# call main
if __name__ == '__main__':
    main()
