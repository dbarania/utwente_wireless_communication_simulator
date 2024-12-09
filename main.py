from simulation import Simulation

config_file = "config.yaml"
if __name__ == "__main__":
    sim = Simulation()
    sim.setup_simulation(config_file)
    sim.run()
