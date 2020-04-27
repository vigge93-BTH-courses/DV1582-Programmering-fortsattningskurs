import simsimsui
import place
import transition


class Simulation():
    '''The class that manages the simulation and keeps track of all objects in the simulation.'''
    gui = None

    def __init__(self, initial_workers=0):
        self.create_gui()
        self._road = place.Road(initial_workers)
        self._shed = place.Shed()
        self._magazine = place.Magazine()
        self._transitions = []

    @property
    def get_road(self):
        '''Returns the road.'''
        return self._road

    @property
    def get_shed(self):
        '''Returns the shed.'''
        return self._shed

    @property
    def get_magazine(self):
        '''Returns the magazine.'''
        return self._magazine

    def create_gui(self):
        '''Creates a gui class attribute.'''
        Simulation.gui = simsimsui.SimSimsGUI(w=400, h=400)
        Simulation.gui.on_shoot(self.stop)

    def update_gui(self):
        '''Updates position of all gui elements.'''
        num_of_gui_objects = len(self._transitions) + 3
        self._road.get_gui_component.autoplace(0, num_of_gui_objects)
        self._shed.get_gui_component.autoplace(1, num_of_gui_objects)
        self._magazine.get_gui_component.autoplace(2, num_of_gui_objects)
        for idx, transition in enumerate(self._transitions):
            transition.get_gui_component.autoplace(idx + 3, num_of_gui_objects)
        Simulation.gui.update()

    # TODO Start process
    def add_transition(self, trans):
        '''Adds a transition to the simulation and starts its process.'''
        self._transitions.append(trans)

        gui = Simulation.gui
        road_gui = self._road.get_gui_component
        magazine_gui = self._magazine.get_gui_component
        shed_gui = self._shed.get_gui_component
        transition_gui = trans.get_gui_component

        gui.connect(road_gui, transition_gui, {'arrows': False})

        if type(trans) is transition.Apartment:
            gui.connect(transition_gui, magazine_gui, {'arrows': True})
        elif type(trans) is transition.Factory:
            gui.connect(magazine_gui, transition_gui, {'arrows': True})
        elif type(trans) is transition.Farmland:
            gui.connect(shed_gui, transition_gui, {'arrows': True})
        elif type(trans) is transition.Foodcourt:
            Simulation.gui.connect(transition_gui, shed_gui, {
                                   'arrows': True, 'color': '#00AA00'})
        else:
            raise TypeError

    def remove_transition(self, transition):
        '''Ends transition's process and removes it from the simulation.'''
        pass

    def start(self):
        '''Starts the simulation.'''
        pass

    def stop(self):
        '''Stops the simulation.'''
        print('Stop')

    def adapt(self):
        '''Adds or removes transitions and changes priority of apartments in order to balance the system.'''
        pass

    def to_dict(self):
        '''Serializes the simulation object to a dictionary.'''
        return {
            'road': self._road.to_dict(),
            'shed': self._shed.to_dict(),
            'magazine': self._magazine.to_dict(),
            'transitions': [transition.to_dict() for transition in self._transitions]
        }

    # TODO Add transitions to simulation
    @classmethod
    def from_dict(cls, data):
        '''Creates a simulation object from a dictionary.'''
        sim = cls()
        road = place.Road.from_dict(data['road'])
        shed = place.Shed.from_dict(data['shed'])
        magazine = place.Magazine.from_dict(data['magazine'])
        sim._road = road
        sim._shed = shed
        sim._magazine = magazine
        return sim
