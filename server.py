from task import Task, TaskStatus


class Server:
    _time_function = None

    def __init__(self, name: str, operations: int, bandwidth: int, delay: int):
        self.name = name
        self.operations = operations
        self.bandwidth = bandwidth
        self.delay = delay
        self.active_tasks = []

    def load_task(self, task: Task, bandwidth_allocated: int, computation_allocated: int):
        self.active_tasks.append((task, bandwidth_allocated, computation_allocated))
        task.arrival_time = self._time() + self.delay
        task.status = TaskStatus.SENDING
        task.server_responsible = self

    def update_tasks(self):
        for task, bandwidth, computation in self.active_tasks:
            match task.status:
                case TaskStatus.WAITING:
                    raise ValueError("How did this happen!? Needs an investigation")
                case TaskStatus.SENDING:
                    if self._time() >= task.arrival_time:
                        task.update_data_to_send(bandwidth)
                        if task.data_to_send == 0:
                            task.status = TaskStatus.COMPUTING

                case TaskStatus.COMPUTING:
                    task.update_computation_required(computation)
                    if task.computation_required == 0:
                        task.status = TaskStatus.FINISHED
        self._handle_finished_tasks()

    def _handle_finished_tasks(self):
        self.active_tasks = [(t, bw, cmp) for (t, bw, cmp) in self.active_tasks
                             if not (t.status == TaskStatus.FINISHED and self._process_finished_tasks(t, bw, cmp))]

    def _process_finished_tasks(self, task, bandwidth, cpu):
        # TODO implement something
        print(task)
        print(bandwidth)
        print(cpu)
        return True

    @staticmethod
    def from_dict(server_config: dict):
        name = "name"
        operations = "operations"
        bandwidth = "bandwidth"
        delay = "delay"
        return Server(server_config[name], server_config[operations], server_config[bandwidth], server_config[delay])

    @staticmethod
    def _time() -> int:
        return Server._time_function()
