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
        self.data_to_send = data_to_send
        self.privacy_lvl = privacy_lvl
        self.computation_required = computation_required
        self.deadline = self._time() + time_budget
        self.arrival_time = None  # arrival of first packets at the server

    def update_data_to_send(self, bandwidth_allocated: int) -> None:
        self.data_to_send = max(0, self.data_to_send - bandwidth_allocated)

    def update_computation_required(self, cpu_allocated) -> None:
        self.computation_required = max(0, self.computation_required - cpu_allocated)

    @staticmethod
    def _assign_id() -> int:
        Task._id_counter += 1
        return Task._id_counter

    @staticmethod
    def _time() -> int:
        return Task._time_function()
