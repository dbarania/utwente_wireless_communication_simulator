import random
from task import Task


class TaskGenerator:
    _time_function = None

    def __init__(self, data_sizes: list, time_budgets: list, required_computations: list, privacy: list):
        self.data_size_lower = min(data_sizes)
        self.data_size_upper = max(data_sizes)
        self.time_budget_lower = min(time_budgets)
        self.time_budget_upper = max(time_budgets)
        self.required_computation_lower = min(required_computations)
        self.required_computation_upper = max(required_computations)
        self.privacy_lower = min(privacy)
        self.privacy_upper = max(privacy)

    def new_task(self):
        data_size = random.randint(self.data_size_lower, self.data_size_upper)
        time_budget = random.randint(self.time_budget_lower, self.time_budget_upper)
        required_computation = random.randint(self.required_computation_lower, self.required_computation_upper)
        privacy = random.randint(self.privacy_lower, self.privacy_upper)
        return Task(data_size, privacy, required_computation, time_budget)

    @staticmethod
    def from_dict(generator_config: dict):
        data_size = "data_size"
        time_budget = "time_budget"
        required_computation = "required_computation"
        privacy_level = "privacy_level"
        return TaskGenerator(generator_config[data_size], generator_config[time_budget],
                             generator_config[required_computation], generator_config[privacy_level])

    @staticmethod
    def _time():
        return TaskGenerator._time_function()
