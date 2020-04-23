import simsimsui


class Simulation():
    gui = None

    def __init__(self):
        pass

    def create_gui(self):
        Simulation.gui = simsimsui.SimSimsGUI(w=400, h=400)
        Simulation.gui.on_shoot(self.stop)

    def stop(self):
        print('Stop')
