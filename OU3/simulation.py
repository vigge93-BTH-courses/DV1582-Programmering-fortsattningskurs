"""Module for running a petri net simulation following SimSims rules."""
import json
from threading import Thread, Lock, Event

import arc
import place
import simsimsui
import transition


class Simulation(Thread):
    """Manages and keeps track of all objects in the simulation."""

    def __init__(self, save_file, initial_workers=0):
        """Initialize Simulation."""
        Thread.__init__(self)
        self._gui = None
        self._create_gui()

        self._arc = arc.Arc(self)
        self._road = place.Road(initial_workers, self._gui)
        self._shed = place.Shed(self._gui)
        self._magazine = place.Magazine(self._gui)
        self._transitions = []

        self._save_file = save_file
        self._running = False
        self._lock = Lock()
        self._timer = Event()

    @property
    def get_road(self):
        """Return the road."""
        return self._road

    @property
    def get_shed(self):
        """Return the shed."""
        return self._shed

    @property
    def get_magazine(self):
        """Return the magazine."""
        return self._magazine

    @property
    def get_arc(self):
        """Return the arc."""
        return self._arc

    @property
    def get_gui(self):
        """Return the gui."""
        return self._gui

    def get_num_of_transitions(self, trans_type):
        """Return the number of transitions of a specific type."""
        return len([trans for trans in self._transitions
                    if isinstance(trans, trans_type)])

    def get_transition(self, trans_type):
        """Return the first occurence of transition with type: trans_type."""
        for trans in self._transitions:
            if isinstance(trans, trans_type):
                return trans

    def _create_gui(self):
        """Create a gui class attribute."""
        self._gui = simsimsui.SimSimsGUI(w=700, h=700)
        self._gui.on_shoot(self.stop)

    def update_gui_positions(self):
        """Update positions of all gui elements."""
        self._lock.acquire()

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

        for idx, trans in enumerate(self._transitions, 3):
            trans.lock()
            trans.get_gui_component.autoplace(idx, num_of_gui_objects)
            trans.release()

        self._lock.release()

    def add_transition(self, trans):
        """Add a transition to the simulation.

        Start its process if the simulation is running.
        """
        self._lock.acquire()
        self._road.lock()
        self._shed.lock()
        self._magazine.lock()
        trans.lock()

        self._transitions.append(trans)

        road_gui = self._road.get_gui_component
        magazine_gui = self._magazine.get_gui_component
        shed_gui = self._shed.get_gui_component
        transition_gui = trans.get_gui_component

        self._gui.connect(road_gui, transition_gui, {'arrows': True})
        self._gui.connect(transition_gui, road_gui, {'arrows': True})

        if isinstance(trans, transition.Apartment):
            self._gui.connect(magazine_gui, transition_gui, {
                'arrows': True, 'color': '#6666ff'})
        elif isinstance(trans, transition.Factory):
            self._gui.connect(transition_gui, magazine_gui, {
                'arrows': True, 'color': '#6666ff'})
        elif isinstance(trans, transition.Farmland):
            self._gui.connect(transition_gui, shed_gui, {
                'arrows': True, 'color': '#00AA00'})
        elif isinstance(trans, transition.Foodcourt):
            self._gui.connect(shed_gui, transition_gui, {
                'arrows': True, 'color': '#00AA00'})

        self._lock.release()
        self._road.release()
        self._shed.release()
        self._magazine.release()
        trans.release()

        self.update_gui_positions()

        if self._running:
            trans.start()

    def remove_transition(self, trans):
        """End transition's process and remove it from the simulation."""
        trans.finish_thread()
        trans.join()

        self._lock.acquire()
        trans.lock()

        self._gui.remove(trans.get_gui_component)
        self._transitions.remove(trans)

        trans.release()
        self._lock.release()

        self.update_gui_positions()

    def run(self):
        """Start the simulation."""
        for trans in self._transitions:
            trans.start()
        self._running = True
        self.update_gui_positions()
        while self._running:
            self.adapt()
            self._timer.wait(10)
        print('Main loop stopped')
        for trans in self._transitions:
            if trans.is_alive():
                trans.join()
        print('Simulation stopped')

    def stop(self):
        """Set flags to stop the simulation. Save the simulation to file."""
        print('Stopping')
        with open(self._save_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.to_dict()))
        self._arc.set_timer()
        for transition in self._transitions:
            transition.finish_thread()
        self._running = False
        self._timer.set()

    def adapt(self):
        """Add/remove transitions or change apartment priority to balance the system."""
        print('Adapting:')
        # Check if any resources need to adapt
        # ROADS - Controlled with apartments
        if self._road.need_to_adapt():
            # If there are too few workers, focus on reproduction or add one apartment
            if self._road.get_amount < place.Place.threshold_min:
                for trans in self._transitions:
                    if isinstance(trans, transition.Apartment):
                        if trans.get_mode == transition.ApartmentMode.MULTIPLY:
                            apartment = transition.Apartment(
                                self._gui, self._arc)
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
            if self._shed.get_amount < place.Place.threshold_min:
                if self.get_num_of_transitions(transition.Foodcourt) > 2:
                    foodcourt = self.get_transition(transition.Foodcourt)
                    self.remove_transition(foodcourt)
                else:
                    self.add_transition(
                        transition.Farmland(self._gui, self._arc))
            # If there are too many food, remove a farmland if possible, otherwise add a foodcourt
            else:
                if self.get_num_of_transitions(transition.Farmland) > 2:
                    farmland = self.get_transition(transition.Farmland)
                    self.remove_transition(farmland)
                else:
                    self.add_transition(
                        transition.Foodcourt(self._gui, self._arc))

        # MAGAZINE - Controlled with factories primarily and apartments secondarily
        if self._magazine.need_to_adapt():
            # If there are too many products, remove a factory is possible, otherwise add an apartment
            if self._magazine.get_amount > place.Place.threshold_max:
                if self.get_num_of_transitions(transition.Factory) > 2:
                    factory = self.get_transition(transition.Factory)
                    self.remove_transition(factory)
                else:
                    self.add_transition(
                        transition.Apartment(self._gui, self._arc))
            # If there are too few products, add a factory
            else:
                self.add_transition(transition.Factory(self._gui, self._arc))

        # Check if there are enough of each transition
        if self.get_num_of_transitions(transition.Apartment) < 2:
            self.add_transition(transition.Apartment(self._gui, self._arc))
        if self.get_num_of_transitions(transition.Factory) < 2:
            self.add_transition(transition.Factory(self._gui, self._arc))
        if self.get_num_of_transitions(transition.Farmland) < 2:
            self.add_transition(transition.Farmland(self._gui, self._arc))
        if self.get_num_of_transitions(transition.Foodcourt) < 2:
            self.add_transition(transition.Foodcourt(self._gui, self._arc))

        print()

    def to_dict(self):
        """Serialize the simulation object to a dictionary."""
        return {
            'road': self._road.to_dict(),
            'shed': self._shed.to_dict(),
            'magazine': self._magazine.to_dict(),
            'transitions': [transition.to_dict()
                            for transition in self._transitions],
        }

    @classmethod
    def from_dict(cls, data, save_file):
        """Create a simulation object from a dictionary."""
        sim = cls(save_file)

        sim._road.remove_gui_component()
        sim._shed.remove_gui_component()
        sim._magazine.remove_gui_component()

        sim._road = place.Road.from_dict(data['road'], sim.get_gui)
        sim._shed = place.Shed.from_dict(data['shed'], sim.get_gui)
        sim._magazine = place.Magazine.from_dict(data['magazine'], sim.get_gui)

        for trans in data['transitions']:
            if trans['type'] == 'foodcourt':
                sim.add_transition(transition.Foodcourt.from_dict(
                    trans, sim.get_gui, sim.get_arc))
            elif trans['type'] == 'farmland':
                sim.add_transition(transition.Farmland.from_dict(
                    trans, sim.get_gui, sim.get_arc))
            elif trans['type'] == 'apartment':
                sim.add_transition(transition.Apartment.from_dict(
                    trans, sim.get_gui, sim.get_arc))
            elif trans['type'] == 'factory':
                sim.add_transition(transition.Factory.from_dict(
                    trans, sim.get_gui, sim.get_arc))

        return sim
