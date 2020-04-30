import json

import simsimsui
import simulation
import arc
import transition


def create_new_sim():
    sim = simulation.Simulation(10)
    arc.Arc.set_simulation(sim)
    return sim


def sim_from_json():
    f = open('sim.json', 'r+', encoding='utf-8')
    sim_str = f.read()
    sim = simulation.Simulation.from_dict(json.loads(sim_str))
    arc.Arc.set_simulation(sim)
    return sim


new_sim = True

if __name__ == '__main__':
    if new_sim:
        sim = create_new_sim()
    else:
        sim = sim_from_json()

    sim.start()

    input()
