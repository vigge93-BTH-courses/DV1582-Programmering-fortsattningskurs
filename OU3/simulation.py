import threading
from time import sleep
import json

import simsimsui
import place
import transition


class Simulation(threading.Thread):
    """The class that manages the simulation and keeps track of all objects in the simulation."""
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
        """Returns the road."""
        return self._road

    @property
    def get_shed(self):
        """Returns the shed."""
        return self._shed

    @property
    def get_magazine(self):
        """Returns the magazine."""
        return self._magazine

    def get_num_of_transitions(self, trans_type):
        """Returns the number of transitions of a specific type."""
        return len([trans for trans in self._transitions if isinstance(trans, trans_type)])

    def get_transition(self, trans_type):
        """Returns the first occurence of transition with type: trans_type in transitions."""
        for trans in self._transitions:
            if isinstance(trans, trans_type):
                return trans

    def create_gui(self):
        """Creates a gui class attribute."""
        Simulation.gui = simsimsui.SimSimsGUI(w=700, h=700)
        Simulation.gui.on_shoot(self.stop)

    def update_gui_positions(self):
        """Updates positions of all gui elements."""
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

    def add_transition(self, trans, /):
        """Adds a transition to the simulation and starts its process if the simulation is running."""
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

        if isinstance(trans, transition.Apartment):
            gui.connect(transition_gui, magazine_gui, {
                        'arrows': True, 'color': '#AA0000'})
        elif isinstance(trans, transition.Factory):
            gui.connect(magazine_gui, transition_gui, {
                        'arrows': True, 'color': '#AA0000'})
        elif isinstance(trans, transition.Farmland):
            gui.connect(shed_gui, transition_gui, {
                        'arrows': True, 'color': '#00AA00'})
        elif isinstance(trans, transition.Foodcourt):
            gui.connect(transition_gui, shed_gui, {
                'arrows': True, 'color': '#00AA00'})

        Simulation.lock.release()
        self._road.release()
        self._shed.release()
        self._magazine.release()
        trans.release()

        self.update_gui_positions()

        if self._running:
            trans.start()

    def remove_transition(self, trans, /):
        """Ends transition's process and removes it from the simulation."""
        trans.finish_thread()
        trans.join()

        Simulation.lock.acquire()
        trans.lock()

        Simulation.gui.remove(trans.get_gui_component)
        self._transitions.remove(trans)

        trans.release()
        Simulation.lock.release()

        self.update_gui_positions()

    def run(self):
        """Starts the simulation."""
        for trans in self._transitions:
            trans.start()
        self._running = True
        self.update_gui_positions()
        while self._running:
            self.adapt()
            with open('sim.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.to_dict()))
            sleep(10)
        print('Main loop stopped')
        for trans in self._transitions:
            trans.join()
        print('Simulation stopped')

    def stop(self):
        """Sets flags to stop the simulation."""
        print('Stopping')
        for transition in self._transitions:
            transition.finish_thread()
        self._running = False

    def adapt(self):
        """Adds or removes transitions and changes priority of apartments in order to balance the system."""
        print('Adapting:')
        # Check if any resources need to adapt
        # ROADS - Controlled with apartments
        if self._road.need_to_adapt():
            # If there are too few workers, focus on reproduction or add one apartment
            if self._road.get_amount < place.Place.min_amount:
                for trans in self._transitions:
                    if isinstance(trans, transition.Apartment):
                        if trans.get_mode == transition.ApartmentMode.MULTIPLY:
                            apartment = transition.Apartment()
                            apartment.set_mode(
                                transition.ApartmentMode.MULTIPLY)
                            self.add_transition(apartment)
                            break
                        trans.set_mode(transition.ApartmentMode.MULTIPLY)

            # If there are too many workers, focus on resting or remove one apartment
            else:
                for trans in self._transitions:
                    if isinstance(trans, transition.Apartment):
                        if trans.get_mode == transition.ApartmentMode.REST:
                            self.remove_transition(trans)
                            break
                        trans.set_mode(transition.ApartmentMode.REST)
        # If there are enough workers, return apartments to neutral state.
        else:
            for trans in self._transitions:
                if isinstance(trans, transition.Apartment):
                    trans.set_mode(transition.ApartmentMode.NEUTRAL)

        # SHEDS - Controlled with farmlands and foodcourts
        if self._shed.need_to_adapt():
            # If there are too few food, remove a foodcourt if possible, otherwise add a farmland
            if self._shed.get_amount < place.Place.min_amount:
                if self.get_num_of_transitions(transition.Foodcourt) > 2:
                    foodcourt = self.get_transition(transition.Foodcourt)
                    self.remove_transition(foodcourt)
                else:
                    self.add_transition(transition.Farmland())
            # If there are too many food, remove a farmland if possible, otherwise add a foodcourt
            else:
                if self.get_num_of_transitions(transition.Farmland) > 2:
                    farmland = self.get_transition(transition.Farmland)
                    self.remove_transition(farmland)
                else:
                    self.add_transition(transition.Foodcourt())

        # MAGAZINE - Controlled with factories primarily and apartments secondarily
        if self._magazine.need_to_adapt():
            # If there are too many products, remove a factory is possible, otherwise add an apartment
            if self._magazine.get_amount > place.Place.max_amount:
                if self.get_num_of_transitions(transition.Factory) > 2:
                    factory = self.get_transition(transition.Factory)
                    self.remove_transition(factory)
                else:
                    self.add_transition(transition.Apartment())
            # If there are too few products, add a factory
            else:
                self.add_transition(transition.Factory())

        # Check if there are enough of each transition
        if self.get_num_of_transitions(transition.Apartment) < 2:
            self.add_transition(transition.Apartment())
        if self.get_num_of_transitions(transition.Factory) < 2:
            self.add_transition(transition.Factory())
        if self.get_num_of_transitions(transition.Farmland) < 2:
            self.add_transition(transition.Farmland())
        if self.get_num_of_transitions(transition.Foodcourt) < 2:
            self.add_transition(transition.Foodcourt())

        print()

    def to_dict(self):
        """Serializes the simulation object to a dictionary."""
        return {
            'road': self._road.to_dict(),
            'shed': self._shed.to_dict(),
            'magazine': self._magazine.to_dict(),
            'transitions': [transition.to_dict() for transition in self._transitions],
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a simulation object from a dictionary."""
        sim = cls()

        sim._road.remove_gui_component()
        sim._shed.remove_gui_component()
        sim._magazine.remove_gui_component()

        sim._road = place.Road.from_dict(data['road'])
        sim._shed = place.Shed.from_dict(data['shed'])
        sim._magazine = place.Magazine.from_dict(data['magazine'])

        for trans in data['transitions']:
            if trans['type'] == 'foodcourt':
                sim.add_transition(transition.Foodcourt.from_dict(trans))
            elif trans['type'] == 'farmland':
                sim.add_transition(transition.Farmland.from_dict(trans))
            elif trans['type'] == 'apartment':
                sim.add_transition(transition.Apartment.from_dict(trans))
            elif trans['type'] == 'factory':
                sim.add_transition(transition.Factory.from_dict(trans))

        return sim
