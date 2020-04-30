import json

import token_simsims as token
import simulation
from gui_node_interface import GUINodeInterface


class Place(GUINodeInterface):
    """Parent class for all places."""
    min_amount = 3
    max_amount = 20

    def __init__(self):
        GUINodeInterface.__init__(self)
        self._tokens = []

    @property
    def get_amount(self):
        """Returns the number of tokens in the container."""
        return len(self._tokens)

    def add(self, token, /):
        """Adds a token to the container."""
        token.lock()
        self.lock()
        self._tokens.append(token)
        self._gui_component.add_token(token.get_gui_component)
        self.release()
        token.release()

    def remove(self):
        """Removes and returns the first token in the container."""
        if len(self._tokens) > 0:
            self.lock()
            token = self._tokens[0]
            token.lock()
            self._gui_component.remove_token(token.get_gui_component)
            self.release()
            token.release()
            self._tokens = self._tokens[1:]
            return token
        else:
            raise RuntimeError('Not enough resources')

    def need_to_adapt(self):
        """Returns True if changes to transitions are needed to balance resources."""
        adapt = not Place.min_amount <= self.get_amount <= Place.max_amount
        print(f'{type(self).__name__} needs to adapt: {adapt}')
        return adapt

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError


class Shed(Place):
    """A place to store food tokens."""

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        """Creates a green shed gui components and adds it to gui."""
        properties = {'lable': 'Shed', 'color': '#00ff00'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_place_ui(
            properties)
        simulation.Simulation.lock.release()
        self.release()

    def to_dict(self):
        """Serializes shed to a dictionary."""
        return {'food': self.get_amount}

    @classmethod
    def from_dict(cls, data):
        """Creates and returns a shed from a dict object."""
        shed = cls()
        for _ in range(data['food']):
            shed.add(token.Food())
        return shed


class Magazine(Place):
    """A place to store product tokens."""

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        """Creates a red magazine gui components and adds it to gui."""
        properties = {'lable': 'Magazine', 'color': '#ff0000'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_place_ui(
            properties)
        simulation.Simulation.lock.release()
        self.release()

    def to_dict(self):
        """Serializes magazine to a dictionary."""
        return {'product': self.get_amount}

    @classmethod
    def from_dict(cls, data):
        """Creates and returns a magazine from a dict object."""
        magazine = cls()
        for _ in range(data['product']):
            magazine.add(token.Product())
        return magazine


class Road(Place):
    """A place to store workers."""

    def __init__(self, initial_workers):
        super().__init__()
        self.create_gui_component()
        for _ in range(initial_workers):
            self.add(token.Worker())

    def add(self, worker, /):
        """Adds a worker to the road and reduces its health proportional to the amount of workers already on the road."""
        # Removes 1% of max health for each worker on the road
        life_to_remove = token.Worker.max_health * 0.01 * self.get_amount
        if not worker.decrease_health(life_to_remove):
            super().add(worker)

    def create_gui_component(self):
        """Creates a black road gui component and adds it to gui."""
        properties = {'lable': 'Road', 'color': '#000000'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_place_ui(
            properties)
        simulation.Simulation.lock.release()
        self.release()

    def to_dict(self):
        """Serializes road to a dictionary."""
        return {'workers': [worker.to_dict() for worker in self._tokens]}

    @classmethod
    def from_dict(cls, data):
        """Creates and returns a magazine from a dict object."""
        road = cls(0)
        for worker in data['workers']:
            worker = token.Worker.from_dict(worker)
            worker.lock()
            road.lock()
            road._tokens.append(worker)
            road.get_gui_component.add_token(worker.get_gui_component)
            road.release()
            worker.release()

        return road
