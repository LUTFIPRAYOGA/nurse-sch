import os
import copy
import pickle
import random
from math import floor, ceil

import numpy as np
from tabulate import tabulate


class Config(object):
    nPar = 3
    nSwarm = 3
    hourPerShift = 8
    maxHourPerMonth = 152
    nSwapDay = 5
    shiftOpt = ['P', 'S', 'M', 'L']
    normalShift = ['P', 'S']


def get_result(ruang):
    module_dir = os.path.dirname(__file__)
    file_path1 = os.path.join(module_dir, 'result', ruang, 'particle.pickle')
    file_path2 = os.path.join(module_dir, 'result', ruang, 'gbest.pickle')
    file_path3 = os.path.join(module_dir, 'result', ruang, 'stats.pickle')
    particles = []
    all_gbest_fitness = []
    all_best_constraint = []
    gb_par = np.empty(0)
    iteration = 0
    if os.path.exists(file_path1) and os.path.exists(file_path2) and os.path.exists(file_path3):
        ##get them
        with open(file_path1, 'rb') as f1:
            particles = pickle.load(f1)
            f1.close()
        with open(file_path2, 'rb') as f2:
            gb_par, iteration = pickle.load(f2)
            f2.close()
        with open(file_path3, 'rb') as f3:
            all_gbest_fitness, all_best_constraint, _ = pickle.load(f3)
            f3.close()

    last_gbest_fitness = None if not all_gbest_fitness else all_gbest_fitness[-1]
    return particles, gb_par.tolist(), last_gbest_fitness, iteration, all_best_constraint


def get_stats(ruang):
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'result', ruang, 'stats.pickle')
    all_gbest_fitness = []
    all_gbest_constraint = []
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            all_gbest_fitness, all_gbest_constraint, _ = pickle.load(f)
            f.close()

    return all_gbest_fitness, all_gbest_constraint


def print_str(array):
    print([''.join(row) for row in array])


def main(maxIter, nurses, ruang, days, state="Start"):
    module_dir = os.path.dirname(__file__)
    last_iteration = 0
    lowest_fitness = 1
    all_gbest_fitness = []
    all_gbest_constraint = []
    if state != "Continue":
        dir_path = os.path.join(module_dir, 'result', ruang)
        lis_dir = os.listdir(dir_path)
        for item in lis_dir:
            if item.endswith(".pickle"):
                os.remove(os.path.join(dir_path, item))
        last_iteration = 0
        lowest_fitness = 1

    numNursePerShift = [floor(nurses/4), ceil(nurses/4)]
    pso = PsoHelper(number_of_nurses=nurses, nurses_per_shift=numNursePerShift, room=ruang, days=days)
    file_path1 = os.path.join(module_dir, 'result', ruang, 'particle.pickle')
    file_path2 = os.path.join(module_dir, 'result', ruang, 'gbest.pickle')
    file_path3 = os.path.join(module_dir, 'result', ruang, 'stats.pickle')
    gb_par = np.empty(0)
    if os.path.exists(file_path1) and os.path.exists(file_path2) and os.path.exists(file_path3):
        ##get them
        with open(file_path1, 'rb') as f1:
            particles = pickle.load(f1)
            f1.close()
        with open(file_path2, 'rb') as f2:
            gb_par, last_iteration = pickle.load(f2)
            f2.close()
        with open(file_path3, 'rb') as f3:
            all_gbest_fitness, all_gbest_constraint, lowest_fitness = pickle.load(f3)
            f3.close()
    else:
        ##init them
        particles = pso.init_particle()

    ## get fitness
    fitness = pso.get_fitness(particles)
    print(tabulate(fitness))

    if gb_par.size:
        print("GBest Particle is exist")
        print_str(gb_par)
        gb_fitness = pso.particle_fitness(gb_par)
    else:
        print("GBest Particle is not exist")
        ## pbest & gbest
        pb_par = pso.get_p_best(fitness, particles)
        gb_par, gb_fitness = pso.get_g_best(pb_par)
        all_gbest_constraint.append([
            pso.first_constrain(gb_par),
            pso.second_contsrain(gb_par),
            pso.third_constrain(gb_par),
            pso.fourth_constrain(gb_par)
        ])
        # print("GBest ", pso.particle_fitness(gb_par), gb_fitness)
        # print_str(gb_par)

    iteration = last_iteration
    stagnant_count = 0
    while True:
        iteration += 1
        current_fitness = copy.deepcopy(pso.particle_fitness(gb_par))
        particles, fitness, gb_par, lowest_fitness, gb_constraint = pso.update_pos(particles, fitness, gb_par, lowest_fitness)
        print("Iteration ", iteration, pso.particle_fitness(gb_par), gb_constraint)
        all_gbest_fitness.append(pso.particle_fitness(gb_par))
        all_gbest_constraint.append(gb_constraint)
        with open(file_path3, 'wb') as f3:
            pickle.dump([all_gbest_fitness, all_gbest_constraint, lowest_fitness], f3)
            f3.close()

        if pso.particle_fitness(gb_par) == current_fitness:
            stagnant_count += 1
        else:
            stagnant_count = 0

        # print(stagnant_count)
        if (iteration == (last_iteration + maxIter)) or (stagnant_count == 10):
        # if (iteration == (last_iteration + maxIter)) :
            with open(file_path2, 'wb') as f1:
                pickle.dump([gb_par, iteration], f1)
                f1.close()
            with open(file_path1, 'wb') as f2:
                pickle.dump(particles, f2)
                f2.close()
            print("Last GBest Particle")
            print_str(gb_par)
            break


# if __name__ == '__main__':
#     main()


class PsoHelper(object):
    def __init__(self, number_of_nurses, nurses_per_shift, room, days):
        self.number_of_nurses = number_of_nurses
        self.nurses_per_shift = nurses_per_shift
        self.room = room
        self.days = days

    def next_el(self, data, i):
        return data[i + 1]

    def prev(self, data, i):
        return data[i - 1]

    def column(self, data, i):
        return [row[i] for row in data]

    def init_particle(self):
        particle = []
        print("Try to generate new file....")
        for i in range(Config.nSwarm):
            parInSwarm = []
            for j in range(Config.nPar):
                parInSwarm.append(np.random.choice(Config.shiftOpt, [self.number_of_nurses, self.days]))
            particle.append(parInSwarm)
        file_path = os.path.join(os.path.dirname(__file__), 'result', self.room, 'init.pickle')
        with open(file_path, 'wb') as f:
            pickle.dump(particle, f)
        return particle

    def particle_fitness(self, particle):
        hard = self.first_constrain(particle) + self.second_contsrain(particle)
        soft = self.third_constrain(particle) + self.fourth_constrain(particle)
        fitness_of_particle = 1 / (1 + (hard * 0.8) + (soft * 0.2))
        return fitness_of_particle

    def get_fitness(self, particles):
        fitness = []
        for i in range(Config.nSwarm):
            fitnessInSwarm = []
            for j in range(Config.nPar):
                f = self.particle_fitness(particles[i][j])
                fitnessInSwarm.append(f)
            fitness.append(fitnessInSwarm)
        return fitness

    def get_p_best(self, fitness, particle):
        pb_par = []
        for i, swarm_fitness in enumerate(fitness):
            best = max(swarm_fitness)
            index = swarm_fitness.index(best)
            print(i, index)
            pb_par.append(particle[i][index])
        return pb_par

    def get_g_best(self, pbest):
        pb_fitness = []
        for i in range(Config.nSwarm):
            pb_fitness.append(self.particle_fitness(pbest[i]))
        best = max(pb_f for pb_f in pb_fitness)
        index = pb_fitness.index(best)
        return pbest[index], best

    def v_particle(self, particle_fitness, gbest_fitness):
        v = (abs(gbest_fitness - particle_fitness)) / gbest_fitness
        return v

    def update_pos(self, particles, all_fitness, gb_par, lowest_fitness):
        current_gb = gb_par
        gb_constraint = [
            self.first_constrain(current_gb),
            self.second_contsrain(current_gb),
            self.third_constrain(current_gb),
            self.fourth_constrain(current_gb)
        ]
        # print(all_fitness)
        # print("Fitness", particle_fitness(current_gb))
        # print([''.join(row) for row in current_gb])
        for i in range(Config.nSwarm):
            for j in range(Config.nPar):
                # print("Current Gb-", particle_fitness(current_gb))
                gb_p = copy.deepcopy(current_gb)
                v = self.v_particle(all_fitness[i][j], self.particle_fitness(gb_p))
                Sp = particles[i][j]
                rand = random.uniform(0, 1)
                if v > rand:
                    Sp = self.nearer(Sp, particles, all_fitness)  ## do nearer
                Sp = self.swap_shift(Sp)  ## do swap-shift
                # print("--------------")
                if self.particle_fitness(Sp) < lowest_fitness:
                    lowest_fitness = copy.deepcopy(self.particle_fitness(Sp))
                # print("Sp", particle_fitness(Sp), isLarger)
                # print(particle_fitness(Sp), [''.join(row) for row in Sp])
                particles[i][j] = Sp
                all_fitness[i][j] = self.particle_fitness(particles[i][j])
                if self.particle_fitness(Sp) >= self.particle_fitness(gb_p):
                    gb_p = copy.deepcopy(Sp)
                    gb_constraint = [
                        self.first_constrain(Sp),
                        self.second_contsrain(Sp),
                        self.third_constrain(Sp),
                        self.fourth_constrain(Sp)
                    ]
                # print("Gb")
                # print(particle_fitness(gb_p))
                # print([''.join(row) for row in gb_p])
                # print(np.array_equal(Sp, gb_p))
                current_gb = copy.deepcopy(gb_p)

        gb_par = copy.deepcopy(current_gb)
        return particles, all_fitness, gb_par, lowest_fitness, gb_constraint

    def swap_shift(self, S_particle):
        if self.number_of_nurses > 5:
            rows = random.sample(range(0, self.number_of_nurses), 6)
            cols = random.sample(range(0, self.days), 15)
            cols.sort()
            a_particle = copy.deepcopy(S_particle)
            for i in range(3):
                a_particle[rows[0]][cols[i]], a_particle[rows[1]][cols[i]] = a_particle[rows[1]][cols[i]], \
                                                                             a_particle[rows[0]][cols[i]]
                a_particle[rows[2]][cols[i]], a_particle[rows[3]][cols[i]] = a_particle[rows[3]][cols[i]], \
                                                                             a_particle[rows[2]][
                                                                                 cols[i]]
                a_particle[rows[4]][cols[i]], a_particle[rows[5]][cols[i]] = a_particle[rows[5]][cols[i]], \
                                                                             a_particle[rows[4]][
                                                                                 cols[i]]
        else:
            rows = random.sample(range(0, self.number_of_nurses), 2)
            cols = random.sample(range(0, self.days), 15)
            cols.sort()
            a_particle = copy.deepcopy(S_particle)
            for i in range(3):
                a_particle[rows[0]][cols[i]], a_particle[rows[1]][cols[i]] = a_particle[rows[1]][cols[i]], \
                                                                             a_particle[rows[0]][cols[i]]
        return a_particle

    def nearer(self, a_particle, particles, fitness):
        goal_fitness = self.particle_fitness(a_particle)
        choice = []
        for row in fitness:
            for item in row:
                if item > goal_fitness:
                    choice.append(item)
        if choice:
            fitness_Sr = random.choice(choice)
            position = np.argwhere(np.array(fitness) == fitness_Sr)
            positionInArray = position.tolist()
            row = positionInArray[0][0]
            col = positionInArray[0][1]
            Sr = particles[row][col]
            S_temp = Sr
            S_temp = self.swap_shift(S_temp)
            if np.array_equal(S_temp, Sr):
                a_particle = copy.deepcopy(S_temp)
        return a_particle

    def first_constrain(self, a_particle):
        num_of_constrain = 0
        for nurse in a_particle:
            for i, day in enumerate(nurse):
                if 0 <= i < len(nurse) - 1:
                    if day == 'M':
                        if not (self.next_el(nurse, i) == 'L'):
                            num_of_constrain += 0.1
                    # if day == 'L':
                    #     if i > 0:
                    #         if not (self.prev(nurse, i) == 'M'):
                    #             num_of_constrain += 1
        # return 1 if num_of_constrain > 0 else 0
        return round(num_of_constrain)

    def second_contsrain(self, a_particle):
        num_of_constrain = 0
        for nurse in a_particle:
            for i, day in enumerate(nurse):
                if 0 <= i < len(nurse) - 1:
                    if (day == 'L') and (self.next_el(nurse, i) == 'L'):
                        if self.prev(nurse, i) == 'M':
                            if i - 1 > 0:
                                if self.prev(nurse, i - 1) in Config.normalShift:
                                    if i - 2 > 0:
                                        if not (self.prev(nurse, i - 2) in Config.normalShift):
                                            num_of_constrain += 0.1
                                    else:
                                        num_of_constrain += 0.1
                                else:
                                    num_of_constrain += 0.1
                            else:
                                num_of_constrain += 0.1
                        else:
                            num_of_constrain += 0.1
        # return 1 if num_of_constrain > 0 else 0
        return round(num_of_constrain)

    def third_constrain(self, a_particle):
        num_of_constrain = 0
        for nurse in a_particle:
            num_of_L = np.count_nonzero(nurse == 'L')
            if ((self.days - num_of_L) * Config.hourPerShift) != Config.maxHourPerMonth:
                num_of_constrain += 0.25
        return round(num_of_constrain)

    def fourth_constrain(self, a_particle):
        num_of_constrain = 0
        for i in range(self.days):
            col = self.column(a_particle, i)
            if (col.count('P') not in self.nurses_per_shift) or (col.count('S') not in self.nurses_per_shift) or (
                    col.count('M') not in self.nurses_per_shift):
                num_of_constrain += 1
        return num_of_constrain
