import json
from token_simsims import Food, Product, Worker
from simulation import Simulation


class Place():
    '''Parent class for all places.'''

    def __init__(self):
        self._gui_component = None
        self._tokens = []

    @property
    def get_amount(self):
        '''Returns the number of tokens in the container.'''
        return len(self._tokens)

    @property
    def get_gui_component(self):
        return self._gui_component

    def add(self, token):
        '''Adds a token to the container.'''
        self._tokens.append(token)

    def remove(self):
        '''Removes and returns the first token in the container.'''
        if len(self._tokens) > 0:
            token = self._tokens[0]
            self._tokens = self._tokens[1:]
            return token
        else:
            raise RuntimeError('Not enough resources')

    def remove_gui_component(self):
        '''Removes place gui component from gui.'''
        Simulation.gui.remove(self._gui_component)

    def need_to_adapt(self):
        raise NotImplementedError

    def create_gui_component(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError


class Shed(Place):
    '''A place to store food tokens.'''

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        '''Creates a green shed gui components and adds it to gui.'''
        properties = {'lable': 'Shed', 'color': '#00ff00'}
        self._gui_component = Simulation.gui.create_place_ui(properties)

    def to_dict(self):
        '''Serializes shed to a JSON-string.'''
        return {'food': self.get_amount}

    @classmethod
    def from_dict(cls, data):
        '''Creates and returns a shed from a json object.'''
        shed = cls()
        for _ in range(data['food']):
            food = Food()
            Simulation.gui.connect(
                shed.get_gui_component, food.get_gui_component)
            shed.add(food)
        return shed


class Magazine(Place):
    '''A place to store product tokens.'''

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        '''Creates a red magazine gui components and adds it to gui.'''
        properties = {'lable': 'Magazine', 'color': '#ff0000'}
        self._gui_component = Simulation.gui.create_place_ui(properties)

    def to_dict(self):
        '''Serializes magazine to a JSON-string.'''
        return {'product': self.get_amount}

    @classmethod
    def from_dict(cls, data):
        '''Creates and returns a magazine from a json object.'''
        magazine = cls()
        for _ in range(data['product']):
            product = Product()
            Simulation.gui.connect(
                magazine.get_gui_component, product.get_gui_component)
            magazine.add(product)
        return magazine


class Road(Place):
    '''A place to store workers'''

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def add(self, worker):
        '''Adds a worker to the road and reduces its health proportional to the amount of workers already on the road.'''
        # Removes 1% of max health for each worker on the road
        life_to_remove = Worker.max_health * 0.01 * self.get_amount
        worker.decrease_health(life_to_remove)
        if worker.get_health > 0:
            self._tokens.append(worker)

    def create_gui_component(self):
        '''Creates a black road gui components and adds it to gui.'''
        properties = {'lable': 'Road', 'color': '#000000'}
        self._gui_component = Simulation.gui.create_place_ui(properties)

    def to_dict(self):
        '''Serializes road to a JSON-string.'''
        return {'workers': [worker.to_dict() for worker in self._tokens]}

    @classmethod
    def from_dict(cls, data):
        '''Creates and returns a magazine from a json object.'''
        road = cls()
        for worker in data['workers']:
            worker = Worker.from_dict(worker)
            Simulation.gui.connect(
                road.get_gui_component, worker.get_gui_component)
            road._tokens.append(worker)
        return road
