import simsimsui
import place
import transition
import threading
from time import sleep
import random
import _thread


class Simulation(threading.Thread):
    '''The class that manages the simulation and keeps track of all objects in the simulation.'''
    gui = None
    lock = threading.Lock()

    def __init__(self, initial_workers=0):
        threading.Thread.__init__(self)
        self.create_gui()
        self._road = place.Road(initial_workers)
        self._shed = place.Shed()
        self._magazine = place.Magazine()
        self._transitions = []
        self._running = False

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

    # @classmethod #https://docs.astropy.org/en/stable/api/astropy.utils.decorators.classproperty.html
    # @property
    # def get_gui(cls):
    #     return cls._gui

    @classmethod
    def update_gui(cls):
        cls.lock.acquire()
        cls.gui.update()
        cls.lock.release()

    def create_gui(self):
        '''Creates a gui class attribute.'''
        Simulation.gui = simsimsui.SimSimsGUI(w=400, h=400)
        Simulation.gui.on_shoot(self.stop)

    def update_gui_positions(self):
        '''Updates position of all gui elements.'''
        Simulation.lock.acquire()

        num_of_gui_objects = len(self._transitions) + 3

        self._road.lock()
        self._road.get_gui_component.autoplace(0, num_of_gui_objects)
        self._road.release()

        self._shed.lock()
        self._shed.get_gui_component.autoplace(1, num_of_gui_objects)
        self._shed.release()

        self._magazine.lock()
        self._magazine.get_gui_component.autoplace(2, num_of_gui_objects)
        self._magazine.release()

        for idx, trans in enumerate(self._transitions):
            trans.lock()
            trans.get_gui_component.autoplace(idx + 3, num_of_gui_objects)
            trans.release()

        Simulation.lock.release()

    def add_transition(self, trans):
        '''Adds a transition to the simulation and starts its process if the simulation is running.'''
        Simulation.lock.acquire()
        self._road.lock()
        self._shed.lock()
        self._magazine.lock()
        trans.lock()

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

        Simulation.lock.release()
        self._road.release()
        self._shed.release()
        self._magazine.release()
        trans.release()
        '''Ends transition's process and removes it from the simulation.'''
        pass

    def start(self):
        '''Starts the simulation.'''
        for trans in self._transitions:
            trans.start()

    def stop(self):
        '''Stops the simulation.'''
        print('Stop')
        for transition in self._transitions:
            transition.finish_thread()

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

    @classmethod
    def from_dict(cls, data):
        '''Creates a simulation object from a dictionary.'''
        sim = cls()
        sim._road.remove_gui_component()
        sim._shed.remove_gui_component()
        sim._magazine.remove_gui_component()
        road = place.Road.from_dict(data['road'])
        shed = place.Shed.from_dict(data['shed'])
        magazine = place.Magazine.from_dict(data['magazine'])
        sim._road = road
        sim._shed = shed
        sim._magazine = magazine
        for trans in data['transitions']:
            if trans['type'] == 'foodcourt':
                sim.add_transition(transition.Foodcourt.from_dict(trans))
            elif trans['type'] == 'farmland':
                sim.add_transition(transition.Farmland.from_dict(trans))
            elif trans['type'] == 'apartment':
                sim.add_transition(transition.Apartment.from_dict(trans))
            elif trans['type'] == 'factory':
                sim.add_transition(transition.Factory.from_dict(trans))
        sim.update_gui()
        return sim
