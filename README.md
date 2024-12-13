# Smart home management simulator

#### Created as a part of Wireless Communication project at the University of Twente in December 2024

## Assumptions about the system

1. Time is represented using discrete time units
2. Data size is represented as an integer
3. Bandwidth is represented as amount of data units transferred to server in a time unit
4. CPU performance is represented as maximum amount operations performed in a time unit
5. There is a data delay between IoT hub and servers represented in time units

There is a list of tasks that still need to be done, inherently each task has the following properties:

- Time frame, how long you have (left) to perform that task, this always runs monotonically with the clock
- Data size, how much data the task uses
- Compute required, how much CPU time is needed to process the task
- Privacy, how sensitive the task is, higher is more sensitive
  First, the data needs to be sent to the smarthub, then it can be processed either on the edge or cloud. At the edge,
  the compute is the limiting factor, at the cloud, the backhaul is the limiting factor, the rest can be neglected. Once
  a task has started edge/cloud calculations, it can no longer be switched (or at least it has to be started all over
  again). When the time frame is over, the task is "overdue" and is no longer executed. When the task is finished, it is
  of course no longer executed.

It should be easy to switch between algorithms, with at least an "edge only", "cloud only", and a proprietary
algorithm (for benchmarking it could be useful to make this easily variable).

An algorithm gets a list of all tasks (can also be a dict), and indicates per task how many resources may be used. The
framework reduces the other parameters of the task. An analysis is done of how heavily occupied the network is. Does
some logging. If necessary, new tasks are created.