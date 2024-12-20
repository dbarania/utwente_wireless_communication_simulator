from simulation import Simulation, DecisionMakingAlgorithm
import random
config_file = "config.yaml"

if __name__ == "__main__":
    sim_custom = Simulation()
    sim_custom.setup_simulation(config_file, DecisionMakingAlgorithm.CUSTOM)
    sim_custom.run()

    sim_edge = Simulation()
    sim_edge.setup_simulation(config_file, DecisionMakingAlgorithm.EVERYTHING_EDGE)
    sim_edge.run()

    sim_cloud = Simulation()
    sim_cloud.setup_simulation(config_file, DecisionMakingAlgorithm.EVERYTHING_CLOUD)
    sim_cloud.run()
