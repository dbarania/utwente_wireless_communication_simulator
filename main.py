from simulation import Simulation
import random

config_file = "config.yaml"

if __name__ == "__main__":
    random.seed(0)
    sim = Simulation()
    sim.setup_simulation(config_file)
    sim.run()
