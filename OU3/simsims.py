import simsimsui
import simulation
import arc
import transition
import sys
import json


if __name__ == "__main__":
    sim = simulation.Simulation(10)
    # f = open('sim.json', 'r+', encoding='utf-8')
    # sim_str = f.read()
    # sim = simulation.Simulation.from_dict(json.loads(sim_str))
    arc.Arc.set_simulation(sim)

    sim.start()

    input()
