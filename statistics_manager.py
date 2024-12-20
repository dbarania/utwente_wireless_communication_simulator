class SystemStateTimestamp:
    _timer = 0

    def __init__(self):
        self.timestamp = SystemStateTimestamp._timer
        SystemStateTimestamp._timer += 1

        self.new_tasks = None
        self.tasks_transferring_edge = None
        self.tasks_transferring_cloud = None
        self.tasks_computing_edge = None
        self.tasks_computing_cloud = None
        self.bandwidth_usage = None
        self.cpu_usage_edge = None
        self.cpu_usage_cloud = None
        self.privacy_edge = None
        self.privacy_cloud = None
        self.tasks_overdue = None

    def update_statistics(self, new_tasks,
                          tasks_transferring_edge,
                          tasks_transferring_cloud,
                          tasks_computing_edge,
                          tasks_computing_cloud,
                          bandwidth_usage,
                          cpu_usage_edge,
                          cpu_usage_cloud,
                          privacy_edge,
                          privacy_cloud,
                          tasks_overdue):
        self.new_tasks = new_tasks
        self.tasks_transferring_edge = tasks_transferring_edge
        self.tasks_transferring_cloud = tasks_transferring_cloud
        self.tasks_computing_edge = tasks_computing_edge
        self.tasks_computing_cloud = tasks_computing_cloud
        self.bandwidth_usage = bandwidth_usage
        self.cpu_usage_edge = cpu_usage_edge
        self.cpu_usage_cloud = cpu_usage_cloud
        self.privacy_edge = privacy_edge
        self.privacy_cloud = privacy_cloud
        self.tasks_overdue = tasks_overdue

    def generate_header(self):
        a = self.__dict__.keys()
        return ','.join(a) + '\n'

    def generate_entry(self):
        return ','.join([str(self.__getattribute__(name)) for name in self.__dict__.keys()]) + '\n'
        # return (f'{self.timestamp},'
        #         f' {self.new_tasks},'
        #         f' {self.tasks_transferring_edge},'
        #         f' {self.tasks_transferring_cloud},'
        #         f' {self.tasks_computing_edge},'
        #         f' {self.tasks_computing_cloud},'
        #         f' {self.bandwidth_usage},'
        #         f' {self.cpu_usage_edge},'
        #         f' {self.cpu_usage_cloud},'
        #         f' {self.privacy_edge},'
        #         f' {self.privacy_cloud}'
        #         f'\n')


class StatisticsManager:
    def __init__(self, num_iterations):
        SystemStateTimestamp._timer = 0
        self.tasks_in_system = []
        self.finished_tasks = []
        self.simulation_to_track = None
        self.state_of_system = [SystemStateTimestamp() for _ in range(num_iterations)]

    def generate_logs(self, log_name: str):
        with open(log_name, 'w') as log_file:
            for timestamp in self.state_of_system:
                if timestamp.timestamp == 0:
                    log_file.write(timestamp.generate_header())
                entry = timestamp.generate_entry()
                log_file.write(entry)
