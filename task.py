from enum import Enum


class TaskStatus(Enum):
    WAITING = 1
    SENDING = 2
    COMPUTING = 3
    FINISHED = 4


class Task:
    _id_counter = 0
    _time_function = None

    def __init__(self, data_to_send: int, privacy_lvl: int, computation_required: int, time_budget: int):
        self.id = self._assign_id()
        self.status = TaskStatus.WAITING

        self.data_size = data_to_send
        self.data_to_send = data_to_send

        self.privacy_lvl = privacy_lvl

        self.computation_required = computation_required
        self.computation_left = computation_required

        self.deadline = self._time() + time_budget

        self._overdue = False
        self.cpu_allocated = None
        self.bandwidth_allocated = None
        self.arrival_time = None
        self.server_responsible = None

    def update_task(self):
        if self.status == TaskStatus.WAITING:
            pass
        elif self.status == TaskStatus.SENDING:
            self._update_data_to_send()
            if self.data_to_send == 0:
                self.status = TaskStatus.COMPUTING
        elif self.status == TaskStatus.COMPUTING:
            if self._time() >= self.arrival_time:
                self._update_computation_left()
                if self.computation_left == 0:
                    self.status = TaskStatus.FINISHED

    def update_cpu(self, cpu: int):
        if cpu > 0:
            self.cpu_allocated = cpu
        else:
            raise ValueError("Cannot allocate 0 operations in a cycle to the task")

    def update_bandwidth(self, bandwidth: int):
        if bandwidth > 0:
            self.bandwidth_allocated = bandwidth
        else:
            raise ValueError("Cannot allocate 0 bandwidth in a cycle to the task")

    def update_server(self, server):
        self.server_responsible = server

    def _update_data_to_send(self) -> None:
        self.data_to_send = max(0, self.data_to_send - self.bandwidth_allocated)

    def _update_computation_left(self) -> None:
        self.computation_left = max(0, self.computation_left - self.cpu_allocated)

    @property
    def overdue(self):
        self._overdue = self._time() > self.deadline and self.status != TaskStatus.FINISHED
        return self._overdue

    @staticmethod
    def _assign_id() -> int:
        Task._id_counter += 1
        return Task._id_counter

    @staticmethod
    def _time() -> int:
        return Task._time_function()

    def reset(self):
        self._id_counter = 0
