import yaml
from task import Task, TaskStatus
from server import Server
from task_generator import TaskGenerator
from decision_making import decision_making_algorithm


class Simulation:

    def __init__(self):
        self._time = 0
        Server._time_function = self.sim_time
        Task._time_function = self.sim_time
        TaskGenerator._time_function = self.sim_time
        self.edge_server = None
        self.cloud_server = None
        self.other_servers = []
        self.target_system_load = None
        self.iterations = None
        self.duration = None
        self.task_generator = None
        self.all_tasks_list = []

    def _create_servers(self, servers_config: list):
        for server_info in servers_config:
            new_server = Server.from_dict(server_info)
            if new_server.name == "Edge server":
                self.edge_server = new_server
            elif new_server.name == "Cloud server":
                self.cloud_server = new_server
            else:
                self.other_servers.append(new_server)

    def _create_task_generator(self, generator_config: dict):
        generator = TaskGenerator.from_dict(generator_config)
        self.task_generator = generator

    def setup_simulation(self, conf_file_path: str):
        target_load = "target_load"
        iterations = "iterations"
        duration = "duration"
        servers = "servers"
        generated_tasks = "generated_tasks"

        with open(conf_file_path) as f:
            config = yaml.safe_load(f)

        simulation_config = config["simulation"]
        self._create_servers(simulation_config[servers])
        self._create_task_generator(simulation_config[generated_tasks])
        self.target_system_load = int(self.edge_server.operations * simulation_config[target_load])
        self.iterations = simulation_config[iterations]
        self.duration = simulation_config[duration]

    def _get_system_load(self):
        return sum(task.computation_required for task in self.all_tasks_list
                   if task.status != TaskStatus.FINISHED)

    def _get_system_load_float(self):
        current_system_load = self._get_system_load()
        assert isinstance(self.edge_server, Server)
        target_system_load = self.edge_server.operations
        return current_system_load / target_system_load

    def reset_simulation(self):
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        self.edge_server.active_tasks = []
        self.cloud_server.active_tasks = []
        self.all_tasks_list = []
        self._time = 0

    def manage_tasks(self):
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        # Adjust this function call to your own algorithm
        # Your function must return 2 lists of dictionaries in
        # {"task": Task_obj, "bandwidth_allocated": bw, "cpu_allocated":cpu} format and
        # a list of Task objects that aren't decided in this timeslot.
        # In case of no new tasks, lists can be empty

        edge_tasks, cloud_tasks, undecided_tasks = decision_making_algorithm()
        for task_specs in edge_tasks:
            task = task_specs["task"]
            bw = task_specs["bandwidth_allocated"]
            cpu = task_specs["cpu_allocated"]
            self.edge_server.load_task(task, bw, cpu)

        for task_specs in cloud_tasks:
            task = task_specs["task"]
            bw = task_specs["bandwidth_allocated"]
            cpu = task_specs["cpu_allocated"]
            self.cloud_server.load_task(task, bw, cpu)

        # TODO handle somehow undecided tasks

    def run(self):
        # # deal with this coeff
        # tunable_coefficient = 4 / 5
        assert isinstance(self.task_generator, TaskGenerator)
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)

        for iteration in range(self.iterations):
            for time_slot in range(self.duration):

                # while self._get_system_load() < tunable_coefficient * self.target_system_load:
                while self._get_system_load() < self.target_system_load:
                    new_task = self.task_generator.new_task()
                    self.all_tasks_list.append(new_task)

                self.manage_tasks()
                self.edge_server.update_tasks()
                self.cloud_server.update_tasks()
                self._time += 1
            self.reset_simulation()

    def sim_time(self):
        return self._time
