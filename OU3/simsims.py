import json

import simulation


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
    sims = []
    if new_sim:
        for i in range(2):
            sims.append(create_new_sim(f'sim{i}.json'))
    else:
        sims.append(sim_from_json('sim0.json', 'sim.json'))
        sims.append(sim_from_json('sim1.json', 'sim2.json'))

    for sim in sims:
        sim.start()

    all_threads_closed = False
    while not all_threads_closed:
        input()
        all_threads_closed = True
        for sim in sims:
            if sim.is_alive():
                all_threads_closed = False
        if not all_threads_closed:
            print('Please close all windows before exiting.', end='')

    for sim in sims:
        sim.join()
