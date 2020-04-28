import simsimsui
import simulation
import arc
import json
import transition
import sys

if __name__ == "__main__":
    sim = simulation.Simulation(10)

    # sim.add_transition(transition.Farmland())
    # sim.add_transition(transition.Farmland())
    # sim.add_transition(transition.Farmland())
    # sim.add_transition(transition.Foodcourt())
    # sim.add_transition(transition.Foodcourt())
    # sim.add_transition(transition.Factory())
    # sim.add_transition(transition.Factory())
    # sim.add_transition(transition.Factory())
    # sim.add_transition(transition.Apartment())
    # sim.add_transition(transition.Apartment())

    arc.Arc.set_simulation(sim)

    sim.start()

    input()
