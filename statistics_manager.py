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

    def update_statistics(self, new_tasks,
                          tasks_transferring_edge,
                          tasks_transferring_cloud,
                          tasks_computing_edge,
                          tasks_computing_cloud,
                          bandwidth_usage,
                          cpu_usage_edge,
                          cpu_usage_cloud,
                          privacy_edge,
                          privacy_cloud):
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


class StatisticsManager:
    def __init__(self, num_iterations):
        self.tasks_in_system = []
        self.finished_tasks = []
        self.simulation_to_track = None
        self.state_of_system = [SystemStateTimestamp() for _ in range(num_iterations)]
