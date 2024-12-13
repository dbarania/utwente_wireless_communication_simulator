from task import Task, TaskStatus


class Hub:
    def __init__(self, bandwidth: int):
        self.bandwidth_limit = bandwidth
        self._bandwidth_allocated = 0
        self.undecided_tasks_list = []
        self.transferred_tasks_list = []

    def add_new_task(self, task: Task):
        self.undecided_tasks_list.append(task)

    def update(self):
        self._move_tasks_to_transferred()
        for t in self.transferred_tasks_list:
            assert isinstance(t, Task)
            t.update_task()
            if t.status == TaskStatus.COMPUTING:
                t.server_responsible.load_task(t)

    @property
    def bandwidth_allocated(self):
        return sum(t.bandwidth_allocated for t in self.transferred_tasks_list)

    def workload_remaining(self):
        return sum(t.computation_required for t in self.undecided_tasks_list)

    def _move_tasks_to_transferred(self):
        for t in self.undecided_tasks_list:
            if t.server_responsible is not None:
                self.transferred_tasks_list.append(t)
                t.server_responsible.transferring_tasks.add_transferring_task(t)
        self.undecided_tasks_list = [t for t in self.undecided_tasks_list if t.server_responsible is None]

    def reset(self):
        self._bandwidth_allocated = 0
        self.undecided_tasks_list.clear()
        self.transferred_tasks_list.clear()
