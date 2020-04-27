import simsimsui
import simulation
import arc
import json
import transition

if __name__ == "__main__":
    sim = simulation.Simulation(5)

    sim.add_transition(transition.Farmland())
    sim.add_transition(transition.Foodcourt())
    sim.add_transition(transition.Factory())
    sim.add_transition(transition.Apartment())

    arc.Arc.set_simulation(simulation)

    sim.update_gui()
    s = json.dumps(sim.to_dict())
    print(s)
    sim2 = simulation.Simulation.from_dict(json.loads(s))
    print(json.dumps(sim2.to_dict()))
    input()
