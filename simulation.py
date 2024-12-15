from enum import Enum
import yaml
from task import Task, TaskStatus
from server import Server
from task_generator import TaskGenerator
import decision_making
from hub import Hub
from statistics_manager import SystemStateTimestamp, StatisticsManager


class DecisionMakingAlgorithm(Enum):
    CUSTOM = 0
    EVERYTHING_EDGE = 1
    EVERYTHING_CLOUD = 2


class Simulation:

    def __init__(self):
        self._time = 0
        Server._time_function = self.sim_time
        Task._time_function = self.sim_time
        TaskGenerator._time_function = self.sim_time
        self.statistics_manager = None
        self.task_generator = None
        self.iot_hub = None
        self.edge_server = None
        self.cloud_server = None

        self.algorithm_used = None
        self.target_system_load = None
        self.iterations = None
        self.duration = None

    def setup_simulation(self, conf_file_path: str, algorithm_mode: DecisionMakingAlgorithm):
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
        self.statistics_manager = StatisticsManager(self.duration)
        self.algorithm_used = algorithm_mode

    def run(self):
        assert isinstance(self.task_generator, TaskGenerator)
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)

        for iteration in range(self.iterations):
            for time_slot in range(self.duration):
                new_tasks = 0
                while self._get_system_load() < self.target_system_load:
                    new_task = self.task_generator.new_task()
                    self.iot_hub.add_new_task(new_task)
                    new_tasks += 1

                self.manage_tasks()
                self.update_tasks()
                self._update_statistics(new_tasks)
                self._time += 1
            self.reset_simulation()

    def manage_tasks(self):
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)

        result = []

        # Probably useful data
        hub = self.iot_hub
        edge_server = self.edge_server
        cloud_server = self.cloud_server

        tasks_to_decide = hub.undecided_tasks_list[:]
        bw_allocated = hub.bandwidth_allocated
        bw_limit = hub.bandwidth_limit
        edge_cpu_allocated = edge_server.cpu_allocated
        edge_cpu_limit = edge_server.operations_limit
        edge_delay = edge_server.delay
        cloud_cpu_allocated = cloud_server.cpu_allocated
        cloud_cpu_limit = cloud_server.operations_limit
        cloud_delay = cloud_server.delay

        # result should be a list of dictionaries where dictionary represents decision made for a task
        # single element of result list:
        # {"task": task,
        # "server": "cloud" | "edge",
        # "bandwidth": bandwidth_to_allocate_to_task,
        # "cpu": cpu_operations_in_time_unit_to_allocate}
        if self.algorithm_used == DecisionMakingAlgorithm.CUSTOM:
            result = decision_making.decision_making_algorithm(self.sim_time(),
                                                               tasks_to_decide,
                                                               bw_allocated,
                                                               bw_limit,
                                                               edge_cpu_allocated,
                                                               edge_cpu_limit,
                                                               edge_delay,
                                                               cloud_cpu_allocated,
                                                               cloud_cpu_limit,
                                                               cloud_delay)
        elif self.algorithm_used == DecisionMakingAlgorithm.EVERYTHING_EDGE:
            result = decision_making.edge_everything_algorithm(self.sim_time(),
                                                               tasks_to_decide,
                                                               bw_allocated,
                                                               bw_limit,
                                                               edge_cpu_allocated,
                                                               edge_cpu_limit,
                                                               edge_delay,
                                                               cloud_cpu_allocated,
                                                               cloud_cpu_limit,
                                                               cloud_delay)
        elif self.algorithm_used == DecisionMakingAlgorithm.EVERYTHING_CLOUD:
            result = decision_making.cloud_everything_algorithm(self.sim_time(),
                                                                tasks_to_decide,
                                                                bw_allocated,
                                                                bw_limit,
                                                                edge_cpu_allocated,
                                                                edge_cpu_limit,
                                                                edge_delay,
                                                                cloud_cpu_allocated,
                                                                cloud_cpu_limit,
                                                                cloud_delay)

        for record in result:
            task, bandwidth, cpu = record["task"], record["bandwidth"], record["cpu"]
            server = self.edge_server if record["server"] == "edge" else self.cloud_server
            assert isinstance(task, Task)
            task.update_cpu(cpu)
            task.update_bandwidth(bandwidth)
            task.update_server(server)
            task.status = TaskStatus.SENDING

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

    def _update_statistics(self, new_tasks_num):
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)
        assert isinstance(self.statistics_manager, StatisticsManager)
        new_tasks = new_tasks_num
        tasks_transferring_edge = len(self.edge_server.transferring_tasks)
        tasks_transferring_cloud = len(self.cloud_server.transferring_tasks)
        tasks_computing_edge = len(self.edge_server.computing_tasks)
        tasks_computing_cloud = len(self.cloud_server.computing_tasks)
        bandwidth_usage = self.iot_hub.bandwidth_allocated
        cpu_usage_edge = self.edge_server.cpu_allocated
        cpu_usage_cloud = self.cloud_server.cpu_allocated
        privacy_edge = self.edge_server.sum_privacy()
        privacy_cloud = self.cloud_server.sum_privacy()
        self.statistics_manager.state_of_system[self.sim_time()].update_statistics(new_tasks, tasks_transferring_edge,
                                                                                   tasks_transferring_cloud,
                                                                                   tasks_computing_edge,
                                                                                   tasks_computing_cloud,
                                                                                   bandwidth_usage, cpu_usage_edge,
                                                                                   cpu_usage_cloud, privacy_edge,
                                                                                   privacy_cloud)

    def _get_system_load(self):
        assert isinstance(self.edge_server, Server)
        assert isinstance(self.cloud_server, Server)
        assert isinstance(self.iot_hub, Hub)
        return (self.iot_hub.workload_remaining() +
                self.edge_server.get_workload +
                self.cloud_server.get_workload)

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
