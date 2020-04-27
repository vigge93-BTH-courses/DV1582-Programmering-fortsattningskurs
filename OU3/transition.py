import simulation
import token_simsims as token
from enum import Enum, auto, unique


class Transition():
    '''Parent class for all transitions.'''

    def __init__(self):
        self._tokens = []
        self._gui_component = None
        self.stop_thread = False

    @property
    def get_gui_component(self):
        '''Returns the transition's gui component.'''
        return self._gui_component

    def run(self):
        '''Starts the thread.'''
        pass

    def finish_thread(self):
        '''Sends a signal to the thread to finish. Returns after thread is done.'''
        pass

    def remove_gui_component(self):
        '''Removes transition gui component from gui.'''
        simulation.Simulation.gui.rmeove(self._gui_component)

    def _get_tokens(self):
        raise NotImplementedError

    def _trigger(self):
        raise NotImplementedError

    def _release_tokens(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def from_dict(self, data):
        raise NotImplementedError


class Foodcourt(Transition):
    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        parameters = {'lable': 'Foodcourt', 'color': '#00FF00'}
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)

    def _get_tokens(self):
        pass

    def _trigger(self):
        pass

    def _release_tokens(self):
        pass

    def to_dict(self):
        data = {'type': 'foodcourt', 'worker': None, 'food': 0}
        for token in self._tokens:
            if type(token) == token.Food:
                data['food'] += 1
            else:
                data['worker'] = token.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        foodcourt = cls()
        if data['worker']:
            worker = token.Worker.from_dict(data['worker'])
            foodcourt._tokens.append(worker)
            foodcourt.get_gui_component.add_token(worker.get_gui_component)

        for _ in range(data['food']):
            food = token.Food()
            foodcourt._tokens.append(food)
            foodcourt.get_gui_component.add_token(food.get_gui_component)
        return foodcourt


class Apartment(Transition):
    def __init__(self):
        super().__init__()
        self.create_gui_component()
        self._mode = ApartmentMode.NEUTRAL

    def create_gui_component(self):
        parameters = {'lable': 'Apartment', 'color': '#000000'}
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)

    def set_mode(self, mode):
        self._mode = mode

    def _get_tokens(self):
        pass

    def _trigger(self):
        pass

    def _release_tokens(self):
        pass

    def to_dict(self):
        data = {'type': 'apartment',
                'workers': [],
                'products': 0,
                'mode': self._mode
                }
        for token in self._tokens:
            if type(token) == token.Product:
                data['products'] += 1
            else:
                data['workers'].append(token.to_dict())
        return data

    @classmethod
    def from_dict(cls, data):
        apartment = cls()
        for worker in data['workers']:
            worker = token.Worker.from_dict(worker)
            apartment._tokens.append(worker)
            apartment.get_gui_component.add_token(worker.get_gui_component)

        for _ in range(data['products']):
            product = token.Product()
            apartment._tokens.append(product)
            apartment.get_gui_component.add_token(product.get_gui_component)

        apartment._mode = data['mode']
        return apartment


class Farmland(Transition):
    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        parameters = {'lable': 'Farmland', 'color': '#9C7200'}
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)

    def _get_tokens(self):
        pass

    def _trigger(self):
        pass

    def _release_tokens(self):
        pass

    def to_dict(self):
        data = {'type': 'farmland', 'worker': None, 'food': 0}
        for token in self._tokens:
            if type(token) == token.Food:
                data['food'] += 1
            else:
                data['worker'] = token.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        farmland = cls()
        if data['worker']:
            worker = token.Worker.from_dict(data['worker'])
            farmland._tokens.append(worker)
            farmland.get_gui_component.add_token(worker.get_gui_component)

        for _ in range(data['food']):
            food = token.Food()
            farmland._tokens.append(food)
            farmland.get_gui_component.add_token(food.get_gui_component)
        return farmland


class Factory(Transition):
    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        parameters = {'lable': 'Factory', 'color': '#ADADAD'}
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)

    def _get_tokens(self):
        pass

    def _trigger(self):
        pass

    def _release_tokens(self):
        pass

    def to_dict(self):
        data = {'type': 'factory', 'worker': None, 'products': 0}
        for token in self._tokens:
            if type(token) == token.Product:
                data['products'] += 1
            else:
                data['worker'] = token.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        factory = cls()
        if 'worker' in data:
            worker = token.Worker.from_dict(data['worker'])
            factory._tokens.append(worker)
            factory.get_gui_component.add_token(worker.get_gui_component)

        for _ in range(data['products']):
            product = token.Product()
            factory._tokens.append(product)
            factory.get_gui_component.add_token(product.get_gui_component)
        return factory


@unique
class ApartmentMode(Enum):
    NEUTRAL = auto()
    REST = auto()
    MULTIPLY = auto()
