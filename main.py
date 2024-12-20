from simulation import Simulation, DecisionMakingAlgorithm
import random
config_file = "config.yaml"

if __name__ == "__main__":
    random.seed(3)
    sim = Simulation()
    sim.setup_simulation(config_file, DecisionMakingAlgorithm.EVERYTHING_EDGE)
    sim.run()
