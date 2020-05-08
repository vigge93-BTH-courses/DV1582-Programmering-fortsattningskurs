"""Module for places that store tokens."""
import json

import token_simsims as token
import simulation
from gui_node_interface import GUINodeInterface


class Place(GUINodeInterface):
    """Parent class for all places."""

    min_amount = 3
    max_amount = 20

    def __init__(self, gui):
        """Initialize place."""
        GUINodeInterface.__init__(self, gui)
        self._tokens = []

    @property
    def get_amount(self):
        """Return the number of tokens in the container."""
        return len(self._tokens)

    def add(self, token, /):
        """Add a token to the container."""
        token.lock()
        self.lock()
        self._tokens.append(token)
        self._gui_component.add_token(token.get_gui_component)
        self.release()
        token.release()

    def remove(self):
        """Remove and return the first token in the container."""
        if len(self._tokens) > 0:
            self.lock()
            token = self._tokens.pop(0)
            token.lock()
            self._gui_component.remove_token(token.get_gui_component)
            self.release()
            token.release()
            return token
        else:
            raise RuntimeError('Not enough resources')

    def need_to_adapt(self):
        """Return True if changes are needed to balance resources."""
        adapt = not Place.min_amount <= self.get_amount <= Place.max_amount
        print(f'{type(self).__name__} needs to adapt: {adapt}')
        return adapt

    def to_dict(self):
        """Abstract method to create a dict from a Place object."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data, gui):
        """Abstract method to create a Place object from a dict."""
        raise NotImplementedError


class Shed(Place):
    """A place to store food tokens."""

    def __init__(self, gui):
        """Initialize Shed."""
        super().__init__(gui)
        self.create_gui_component()

    def create_gui_component(self):
        """Create a green shed gui components and adds it to gui."""
        properties = {'lable': 'Shed', 'color': '#00ff00'}
        self.lock()
        self._gui_component = self._gui.create_place_ui(properties)
        self.release()

    def to_dict(self):
        """Serialize shed to a dictionary."""
        return {'food': self.get_amount}

    @classmethod
    def from_dict(cls, data, gui):
        """Create and return a shed from a dict object."""
        shed = cls(gui)
        for _ in range(data['food']):
            shed.add(token.Food(gui))
        return shed


class Magazine(Place):
    """A place to store product tokens."""

    def __init__(self, gui):
        """Initialize Magazine."""
        super().__init__(gui)
        self.create_gui_component()

    def create_gui_component(self):
        """Create a red magazine gui component and add it to gui."""
        properties = {'lable': 'Magazine', 'color': '#6666ff'}
        self.lock()
        self._gui_component = self._gui.create_place_ui(properties)
        self.release()

    def to_dict(self):
        """Serialize magazine to a dictionary."""
        return {'product': self.get_amount}

    @classmethod
    def from_dict(cls, data, gui):
        """Create and return a magazine from a dict object."""
        magazine = cls(gui)
        for _ in range(data['product']):
            magazine.add(token.Product(gui))
        return magazine


class Road(Place):
    """A place to store workers."""

    def __init__(self, initial_workers, gui):
        """Initialize Road."""
        super().__init__(gui)
        self.create_gui_component()
        for _ in range(initial_workers):
            self.add(token.Worker(gui))

    def add(self, worker, /):
        """Add a worker to the road.

        Reduce its health proportional to the amount
        of workers already on the road.
        """
        # Removes 1% of max health for each worker on the road
        life_to_remove = token.Worker.max_health * 0.01 * self.get_amount
        if not worker.decrease_health(life_to_remove):
            super().add(worker)

    def create_gui_component(self):
        """Create a black road gui component and add it to gui."""
        properties = {'lable': 'Road', 'color': '#000000'}
        self.lock()
        self._gui_component = self._gui.create_place_ui(properties)
        self.release()

    def to_dict(self):
        """Serialize road to a dictionary."""
        return {'workers': [worker.to_dict() for worker
                            in self._tokens if worker.get_health > 0]}

    @classmethod
    def from_dict(cls, data, gui):
        """Create and return a magazine from a dict object."""
        road = cls(0, gui)
        for worker in data['workers']:
            worker = token.Worker.from_dict(worker, gui)
            worker.lock()
            road.lock()
            road._tokens.append(worker)
            road.get_gui_component.add_token(worker.get_gui_component)
            road.release()
            worker.release()

        return road
