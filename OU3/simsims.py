import simsimsui
import simulation

if __name__ == "__main__":
    simulation = simulation.Simulation()
    gui = simsimsui.SimSimsGUI(w=400, h=400)
    gui.on_shoot(simulation.stop())    