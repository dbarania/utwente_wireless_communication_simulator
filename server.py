from task import Task, TaskStatus


class Server:
    _time_function = None

    def __init__(self, name: str, operations: int, delay: int):
        self.name = name
        self.operations_limit = operations
        self.delay = delay
        self.transferring_tasks = []
        self.computing_tasks = []

    def load_task(self, task: Task):
        self.computing_tasks.append(task)
        self.transferring_tasks.remove(task)
        task.arrival_time = self._time() + self.delay
        task.server_responsible = self

    def add_transferring_task(self, task: Task):
        self.transferring_tasks.append(task)

    def reset(self):
        self.transferring_tasks.clear()
        self.computing_tasks.clear()

    def update(self):
        for t in self.computing_tasks:
            assert isinstance(t, Task)
            t.update_task()

    def _handle_finished_tasks(self):
        self.computing_tasks = [t for t in self.computing_tasks
                                if not t.status == TaskStatus.FINISHED and self._process_finished_tasks(t)]

    def _process_finished_tasks(self, task):
        print(task)
        # TODO do some processing
        return True

    @property
    def cpu_allocated(self):
        return sum(t.cpu_allocated for t in
                   [*self.computing_tasks, *self.transferring_tasks])

    @property
    def get_workload(self):
        return sum(t.computation_required for t in
                   [*self.computing_tasks, *self.transferring_tasks])

    def sum_privacy(self):
        return sum(t.privacy_lvl for t in
                   [*self.computing_tasks, *self.transferring_tasks])

    @staticmethod
    def from_dict(server_config: dict):
        name = "name"
        operations = "operations"
        delay = "delay"
        return Server(server_config[name], server_config[operations], server_config[delay])

    @staticmethod
    def _time() -> int:
        return Server._time_function()
