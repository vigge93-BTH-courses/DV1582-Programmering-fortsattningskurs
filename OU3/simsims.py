import json

import simsimsui
import simulation
import arc
import transition


def create_new_sim(save_file):
    """Create and return a new simulation that saves to save_file."""
    sim = simulation.Simulation(save_file, 10)
    return sim


def sim_from_json(load_file, save_file):
    """Create and return a sim from a json-file."""
    with open(load_file, 'r', encoding='utf-8') as f:
        data = f.read()
    sim = simulation.Simulation.from_dict(json.loads(data), save_file)
    return sim


new_sim = True

if __name__ == '__main__':
    if new_sim:
        sim = create_new_sim('sim.json')
        sim2 = create_new_sim('sim2.json')
    else:
        sim = sim_from_json('sim.json', 'sim.json')
        sim2 = sim_from_json('sim2.json', 'sim2.json')

    sim.start()
    sim2.start()

    input()
