import simsimsui
import json


class Token():
    '''Parent class for all tokens.'''

    def __init__(self):
        self._gui_component = None

    @property
    def get_gui_component(self):
        '''Returns tokens gui component.'''
        return self._gui_component

    def remove_gui_component(self, gui):
        '''Removes own gui component from gui.'''
        if self._gui_component:
            gui.remove(self._gui_component)

    def create_gui_component(self, gui):
        raise NotImplementedError


class Product(Token):
    '''Product type token. Subclass to Token.'''

    def __init__(self, gui):
        super().__init__()
        self.create_gui_component(gui)

    def create_gui_component(self, gui):
        '''Creates a red token gui component and adds it to the gui.'''
        properties = {'color': '#ff0000'}
        self._gui_component = gui.create_token_ui(properties)


class Food(Token):
    def __init__(self, gui):
        super().__init__()
        self.create_gui_component(gui)

    def create_gui_component(self, gui):
        '''Creates a green token gui component and adds it to the gui.'''
        properties = {'color': '#00ff00'}
        self._gui_component = gui.create_token_ui(properties)


class Worker(Token):
    max_health = 100

    def __init__(self, gui):
        super().__init__()
        self.create_gui_component(gui)
        self._health = Worker.max_health

    @property
    def get_health(self):
        '''Returns worker's health.'''
        return self._health

    @health.setter
    def health(self, health):
        '''Sets workers health if health is in a valid range, otherwise raises ValueError.'''
        if 0 < health <= Worker.max_health:
            self._health = health
        else:
            raise ValueError

    def create_gui_component(self, gui):
        '''Creates a red token gui component and adds it to the gui.'''
        properties = {'color': '000000'}
        self._gui_component = gui.create_token_ui(properties)

    def decrease_health(self, amount):
        '''Removes health from worker, does not check if worker's health is reduced to or below 0.'''
        self._health -= amount

    def increase_health(self, amount):
        '''Adds health to worker and caps it at the worker's max health.'''
        self._health += amount
        self._health = min(self._health, Worker.max_health)

    def to_json(self):
        '''Serializes worker to a JSON-string.'''
        return json.dumps({'health': self._health})

    @classmethod
    def from_json(cls, data, gui):
        '''Creates and returns a worker from a json object.'''
        worker = cls(gui)
        worker.health = data['health']
        return worker
