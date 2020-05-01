import json

import simulation
from gui_node_interface import GUINodeInterface


class Token(GUINodeInterface):
    """Parent class for all tokens."""

    def __init__(self, gui):
        GUINodeInterface.__init__(self, gui)


class Product(Token):
    """Product type token. Subclass to Token."""

    def __init__(self, gui):
        super().__init__(gui)
        self.create_gui_component()

    def create_gui_component(self):
        """Creates a red token gui component and adds it to the gui."""
        properties = {'color': '#ff0000'}
        self.lock()
        self._gui_component = self._gui.create_token_ui(properties)
        self.release()


class Food(Token):
    """Food type token. Subclass to Token."""

    def __init__(self, gui):
        super().__init__(gui)
        self.create_gui_component()

    def create_gui_component(self):
        """Creates a green token gui component and adds it to the gui."""
        properties = {'color': '#00ff00'}
        self.lock()
        self._gui_component = self._gui.create_token_ui(properties)
        self.release()


class Worker(Token):
    """Worker type token. Subclass to Token."""

    max_health = 100

    def __init__(self, gui):
        super().__init__(gui)
        self.create_gui_component()
        self._health = Worker.max_health

    @property
    def get_health(self):
        """Returns worker's health."""
        return self._health

    @get_health.setter
    def health(self, health):
        """Sets workers health if health is in a valid range, otherwise raises ValueError."""
        if 0 < health <= Worker.max_health:
            self._health = health
        else:
            raise ValueError

    def decrease_health(self, amount):
        """Removes health from worker and returns True if workers health drops to or below 0."""
        self._health -= amount
        return self._health <= 0

    def increase_health(self, amount):
        """Adds health to worker and caps it at the worker's max health."""
        self._health += amount
        self._health = min(self._health, Worker.max_health)

    def create_gui_component(self):
        """Creates a black token gui component and adds it to the gui."""
        properties = {'color': '#000000'}
        self.lock()
        self._gui_component = self._gui.create_token_ui(
            properties)
        self.release()

    def to_dict(self):
        """Serializes worker to a dictionary."""
        return {'health': self._health}

    @classmethod
    def from_dict(cls, data, gui):
        """Creates and returns a worker from a dict object."""
        worker = cls(gui)
        worker.health = data['health']
        return worker
