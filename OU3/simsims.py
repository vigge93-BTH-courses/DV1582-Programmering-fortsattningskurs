import simsimsui
import simulation
from place import Road
from token_simsims import Worker
import json

if __name__ == "__main__":
    simulation = simulation.Simulation()
    simulation.create_gui()
    road = Road()
    for _ in range(5):
        worker = Worker()
        road.add(worker)
    d = road.to_dict()
    print(d)
    r = Road.from_dict(d)
    print(r.to_dict())
