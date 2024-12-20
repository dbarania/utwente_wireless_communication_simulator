import math
from server import Server
from task import Task
from solver import Solver


def decision_making_algorithm(time: int,
                              tasks_to_handle: list[Task],
                              bandwidth_occupied: int,
                              bandwidth_limit: int,
                              edge_cpu_occupied: int,
                              edge_cpu_limit: int,
                              edge_delay: int,
                              cloud_cpu_occupied: int,
                              cloud_cpu_limit: int,
                              cloud_delay: int
                              ):
    bw_available = bandwidth_limit - bandwidth_occupied
    cpu_available_edge = edge_cpu_limit - edge_cpu_occupied
    cpu_available_cloud = cloud_cpu_limit - cloud_cpu_occupied
    while True:
        solver = Solver(tasks_to_handle, bw_available, cpu_available_edge, cpu_available_cloud, edge_delay, cloud_delay)
        result = solver.solve()
        if result is None:
            farthest_task = max(tasks_to_handle, key=lambda t: t.deadline)
            tasks_to_handle.remove(farthest_task)
            if not tasks_to_handle:
                return []
        else:
            return result


def edge_everything_algorithm(time: int,
                              tasks_to_handle: list,
                              bandwidth_occupied: int,
                              bandwidth_limit: int,
                              edge_cpu_occupied: int,
                              edge_cpu_limit: int,
                              edge_delay: int,
                              cloud_cpu_occupied: int,
                              cloud_cpu_limit: int,
                              cloud_delay: int
                              ):
    server_str = "server"
    task_str = "task"
    bandwidth_str = "bandwidth"
    cpu_str = "cpu"
    edge = "edge"

    while True:
        result = []
        bw_available = bandwidth_limit - bandwidth_occupied
        cpu_available = edge_cpu_limit - edge_cpu_occupied
        all_data = sum(t.data_size for t in tasks_to_handle)
        all_operations = sum(t.computation_required for t in tasks_to_handle)
        fail = False
        for task in tasks_to_handle:
            if bw_available == 0:
                fail = True
                break
            avg_time_to_send = max(math.ceil(all_data / bw_available), 1)
            bw_to_allocate = math.ceil(task.data_size / avg_time_to_send)
            time_to_send = math.ceil(task.data_size / bw_to_allocate)
            if time_to_send != avg_time_to_send:
                pass
            time_to_compute_edge = (task.time_budget - time_to_send - edge_delay)
            if time_to_compute_edge <= 0:
                fail = True
                break
            cpu_to_allocate = math.ceil(task.computation_required / time_to_compute_edge)

            if (task.check_task_feasibility(bw_to_allocate, edge_delay, cpu_to_allocate)
                    and bw_available >= bw_to_allocate and cpu_available >= cpu_to_allocate):
                result.append(
                    {task_str: task, server_str: edge, bandwidth_str: bw_to_allocate, cpu_str: cpu_to_allocate})
                cpu_available -= cpu_to_allocate
                bw_available -= bw_to_allocate
                all_data -= task.data_size
            else:
                fail = True
                break
        if fail:
            farthest_task = max(tasks_to_handle, key=lambda t: t.deadline)
            tasks_to_handle.remove(farthest_task)
            continue
        else:
            return result


def cloud_everything_algorithm(time: int,
                               tasks_to_handle: list,
                               bandwidth_occupied: int,
                               bandwidth_limit: int,
                               edge_cpu_occupied: int,
                               edge_cpu_limit: int,
                               edge_delay: int,
                               cloud_cpu_occupied: int,
                               cloud_cpu_limit: int,
                               cloud_delay: int
                               ):
    server_str = "server"
    task_str = "task"
    bandwidth_str = "bandwidth"
    cpu_str = "cpu"
    cloud = "cloud"

    while True:
        result = []
        bw_available = bandwidth_limit - bandwidth_occupied
        cpu_available = cloud_cpu_limit - cloud_cpu_occupied
        all_data = sum(t.data_size for t in tasks_to_handle)
        all_operations = sum(t.computation_required for t in tasks_to_handle)
        fail = False
        for task in tasks_to_handle:
            if bw_available == 0:
                fail = True
                break
            avg_time_to_send = max(math.ceil(all_data / bw_available), 1)
            bw_to_allocate = math.ceil(task.data_size / avg_time_to_send)
            time_to_send = math.ceil(task.data_size / bw_to_allocate)
            if time_to_send != avg_time_to_send:
                pass
            time_to_compute_cloud = (task.time_budget - time_to_send - cloud_delay)
            if time_to_compute_cloud <= 0:
                fail = True
                break
            cpu_to_allocate = math.ceil(task.computation_required / time_to_compute_cloud)

            if (task.check_task_feasibility(bw_to_allocate, cloud_delay, cpu_to_allocate)
                    and bw_available >= bw_to_allocate and cpu_available >= cpu_to_allocate):
                result.append(
                    {task_str: task, server_str: cloud, bandwidth_str: bw_to_allocate, cpu_str: cpu_to_allocate})
                cpu_available -= cpu_to_allocate
                bw_available -= bw_to_allocate
                all_data -= task.data_size
            else:
                fail = True
                break
        if fail:
            farthest_task = max(tasks_to_handle, key=lambda t: t.deadline)
            tasks_to_handle.remove(farthest_task)
            continue
        else:
            return result
