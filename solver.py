import math
import random

from task import Task

bw = "bw"
bandwidth = "bandwidth"
cpu = "cpu"
server = "server"
task = "task"
cloud = "cloud"
edge = "edge"


class Solver:
    def __init__(self, task_list: list[Task], bw_available, edge_cpu_available: int, cloud_cpu_available: int,
                 edge_delay: int, cloud_delay: int):
        self.task_list = task_list
        self.result_proposal = {t.id: {"bw": 0, "cpu": (0, 0), "server": None} for t in task_list}
        self.bw = bw_available
        self.edge_cpu = edge_cpu_available
        self.edge_delay = edge_delay
        self.cloud_cpu = cloud_cpu_available
        self.cloud_delay = cloud_delay

    def allocate_bw_and_propose_cpu(self):
        status = True
        all_data = sum(t.data_size for t in self.task_list)
        bw_available = self.bw
        for t in self.task_list:
            if bw_available == 0:
                return None
            avg_time_to_send = max(math.ceil(all_data / bw_available), 1)
            bw_to_allocate = math.ceil(t.data_size / avg_time_to_send)
            time_to_send = math.ceil(t.data_size / bw_to_allocate)
            if time_to_send != avg_time_to_send:
                pass
                # print("Fore once avg time is different than time to send")
            time_to_compute_edge = (t.time_budget - time_to_send - self.edge_delay)
            time_to_compute_cloud = (t.time_budget - time_to_send - self.cloud_delay)
            if time_to_compute_edge <= 0 and time_to_compute_cloud <= 0:
                return None

            cpu_to_allocate_edge = math.ceil(
                t.computation_required / time_to_compute_edge) if time_to_compute_edge > 0 else 10e9
            cpu_to_allocate_cloud = math.ceil(
                t.computation_required / time_to_compute_cloud) if time_to_compute_cloud > 0 else 10e9

            bw_available -= bw_to_allocate
            all_data -= t.data_size

            self.result_proposal[t.id][bw] = bw_to_allocate
            self.result_proposal[t.id][cpu] = (cpu_to_allocate_edge, cpu_to_allocate_cloud)
        return status

    def _validate_individual(self, individual: list[int]):
        edge_load = 0
        cloud_load = 0
        for i, el in enumerate(individual):
            task_id = self.task_list[i].id
            if el == 0:
                edge_load += self.result_proposal[task_id][cpu][0]
            elif el == 1:
                cloud_load += self.result_proposal[task_id][cpu][1]

        return self.edge_cpu >= edge_load and self.cloud_cpu >= cloud_load

    def _evaluate_individual(self, individual):
        privacy_cost = 0
        penalty = 10e6 if not self._validate_individual(individual) else 0
        for i, el in enumerate(individual):
            if el:
                privacy_cost += self.task_list[i].privacy_lvl
        return penalty + privacy_cost

    def _initialize_population(self, pop_size):
        population = []
        for _ in range(1000):
            individual_proposal = random.choices([0, 1], k=len(self.task_list))
            if self._validate_individual(individual_proposal):
                population.append(individual_proposal)
                if len(population) == pop_size:
                    break

        if not population:
            return None

        elif len(population) < pop_size:
            added_elements = random.choices(population, k=(pop_size - len(population)))
            population += added_elements

        return population

    @staticmethod
    def _crossover(parent1, parent2):
        if len(parent1) == 1:
            return parent2, parent1
        point = random.randint(1, len(parent1) - 1)
        return parent1[:point] + parent2[point:], parent2[:point] + parent1[point:]

    @staticmethod
    def _mutate(individual):
        if len(individual) == 1:
            individual[0] = random.randint(0, 1)
            return individual
        i = random.randint(1, len(individual) - 1)
        individual[i] = 1 - individual[i]
        return individual

    def _evolutionary_algorithm(self, initial_population, pop_size, generations):
        population = initial_population
        best = min(population, key=self._evaluate_individual)[:]
        for _ in range(generations):
            random.shuffle(population)

            fitness = [self._evaluate_individual(ind) for ind in population]

            selected = random.choices(population, weights=[1 / (f+1) for f in fitness], k=pop_size)

            next_population = []
            for i in range(0, pop_size, 2):
                parent1, parent2 = selected[i], selected[i + 1]
                child1, child2 = self._crossover(parent1, parent2)
                next_population.append(self._mutate(child1))
                next_population.append(self._mutate(child2))
            best_in_next_population = min(next_population, key=self._evaluate_individual)[:]
            best = min([best_in_next_population, best], key=self._evaluate_individual)[:]

        return best

    def solve(self):
        status = self.allocate_bw_and_propose_cpu()
        if status is None:
            return None
        pop_size = 12
        generations = 10
        # self.allocate_bw_and_propose_cpu()
        initial_pop = self._initialize_population(pop_size)
        if initial_pop is None:
            return None

        best_solution = self._evolutionary_algorithm(initial_pop, pop_size, generations)
        result = []

        for i, el in enumerate(best_solution):
            task_obj = self.task_list[i]
            task_id = task_obj.id
            bw_for_task = self.result_proposal[task_id][bw]
            cpu_for_task = self.result_proposal[task_id][cpu][el]
            entry = {task: task_obj,
                     server: cloud if el else edge,
                     bandwidth: bw_for_task,
                     cpu: cpu_for_task}
            result.append(entry)
        return result
