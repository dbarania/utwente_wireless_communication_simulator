import yaml
from task import Task, TaskStatus
from server import Server
from task_generator import TaskGenerator
from decision_making import decision_making_algorithm
from hub import Hub


class Simulation:

    def __init__(self):
        self._time = 0
        Server._time_function = self.sim_time
        Task._time_function = self.sim_time
        TaskGenerator._time_function = self.sim_time

        self.task_generator = None
        self.iot_hub = None
        self.edge_server = None
        self.cloud_server = None

        self.target_system_load = None
        self.iterations = None
        self.duration = None

    def setup_simulation(self, conf_file_path: str):
        target_load = "target_load"
        iterations = "iterations"
        duration = "duration"
        bandwidth = "bandwidth"
        servers = "servers"
        generated_tasks = "generated_tasks"

        with open(conf_file_path) as f:
            config = yaml.safe_load(f)

        simulation_config = config["simulation"]
        self._create_servers(simulation_config[servers])
        self._create_task_generator(simulation_config[generated_tasks])
        self.target_system_load = int(self.edge_server.operations_limit * simulation_config[target_load])
        self.iterations = simulation_config[iterations]
        self.duration = simulation_config[duration]
        self.iot_hub = Hub(simulation_config[bandwidth])

    def run(self):
        # # deal with this coeff
        # tunable_coefficient = 4 / 5
        assert isinstance(self.task_generator, TaskGenerator)
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)

        for iteration in range(self.iterations):
            for time_slot in range(self.duration):

                # while self._get_system_load() < tunable_coefficient * self.target_system_load:
                while self._get_system_load() < self.target_system_load:
                    new_task = self.task_generator.new_task()
                    self.iot_hub.add_new_task(new_task)

                self.manage_tasks()
                self.update_tasks()
                self._time += 1
            self.reset_simulation()

    def manage_tasks(self):
        # TODO do something useful with this, mostly rewrite this function
        # This function should only update values of tasks attributes like server, bw and cpu
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)

        # Probably useful data
        hub = self.iot_hub
        edge_server = self.edge_server
        cloud_server = self.cloud_server

        decision_making_algorithm()

    #     Algo needs to output something, probably move tasks within a hub and maybe update their fields

    def update_tasks(self):
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)
        self.edge_server.update()
        self.cloud_server.update()
        self.iot_hub.update()

    def reset_simulation(self):
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)
        self.edge_server.reset()
        self.cloud_server.reset()
        self.iot_hub.reset()
        self._time = 0

    def sim_time(self):
        return self._time

    def _get_system_load(self):
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)
        return sum(t.computation_required for t in
                   [*self.iot_hub.undecided_tasks_list,
                    *self.edge_server.computing_tasks,
                    *self.cloud_server.computing_tasks])

    def _create_servers(self, servers_config: list):
        for server_info in servers_config:
            new_server = Server.from_dict(server_info)
            if new_server.name == "Edge server":
                self.edge_server = new_server
            elif new_server.name == "Cloud server":
                self.cloud_server = new_server

    def _create_task_generator(self, generator_config: dict):
        generator = TaskGenerator.from_dict(generator_config)
        self.task_generator = generator
