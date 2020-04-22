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
    initial_health = 100

    def __init__(self, gui):
        super().__init__()
        self.create_gui_component(gui)
        self._health = Worker.initial_health

    @property
    def get_health(self):
        return self._health

    @health.setter
    def health(self, health):
        if 0 < health <= Worker.initial_health:
            self._health = health
        else:
            raise ValueError

    def create_gui_component(self, gui):
        '''Creates a red token gui component and adds it to the gui.'''
        properties = {'color': '000000'}
        self._gui_component = gui.create_token_ui(properties)

    def decrease_health(self, amount):
        self._health -= amount

    def increase_health(self, amount):
        self._health += amount
        self._health = min(self._health, Worker.initial_health)

    def to_json(self):
        return json.dumps({'health': self._health})

    @classmethod
    def from_json(cls, data, gui):
        worker = cls(gui)
        worker.health = data['health']
        return worker
