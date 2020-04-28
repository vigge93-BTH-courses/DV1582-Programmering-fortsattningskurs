import simulation
import token_simsims as token
from enum import Enum, unique
from GUINodeInterface import GUINodeInterface
from arc import Arc
import random
from time import sleep
from threading import Thread


class Transition(GUINodeInterface, Thread):
    '''Parent class for all transitions.'''

    def __init__(self):
        Thread.__init__(self)
        self._tokens = []
        self.stop_thread = False

    def run(self):
        '''Runs the thread.'''
        while not self.stop_thread:
            if self._get_tokens():
            self._trigger()
            simulation.Simulation.gui.update()
            self._release_tokens()
            else:
                sleep(2)
        self._release_tokens()
        print('thread closed')

    def finish_thread(self):
        '''Sends a signal to the thread to finish. Returns after thread is done.'''
        self.stop_thread = True

    def _add_token(self, token):
        '''Appends a token to the tokens and adds it to the gui.'''
        self._gui_component.add_token(token.get_gui_component)
        self._tokens.append(token)

    def _remove_token(self, token):
        self._gui_component.remove_token(token.get_gui_component)
        self._tokens.remove(token)

    def _get_tokens(self):
        raise NotImplementedError

    def _find_token(self, tpe, /):
        '''Returns the first token of type tpe.'''
        for tok in self._tokens:
            if isinstance(tok, tpe):
                return tok
        return None

    def _trigger(self):
        raise NotImplementedError

    def _release_tokens(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def from_dict(self, data):
        raise NotImplementedError


class Foodcourt(Transition):
    poisoning_risk = 0.05
    min_restore = 5
    max_restore = 25
    production_time = 1

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        parameters = {'lable': 'Foodcourt', 'color': '#00FF00'}
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)

    def _get_tokens(self):
        if not self._find_token(token.Worker):
            worker = Arc.get_worker()
            if worker:
                self._add_token(worker)
        if not self._find_token(token.Food):
            food = Arc.get_food()
            if food:
                self._add_token(food)
        return self._find_token(token.Worker) and self._find_token(token.Food)

    def _trigger(self):
        sleep(Foodcourt.production_time)
        health_diff = random.randint(
            Foodcourt.min_restore, Foodcourt.max_restore)
        if random.random() < Foodcourt.poisoning_risk:
            self._find_token(token.Worker).decrease_health(health_diff)
        else:
            self._find_token(token.Worker).increase_health(health_diff//10)
        self._remove_token(self._find_token(token.Food))

    def _release_tokens(self):
        sleep(Arc.transport_time)
        for tok in self._tokens:
            self._gui_component.remove_token(tok.get_gui_component)
            if isinstance(tok, token.Worker):
            Arc.store_worker(tok)
            elif isinstance(tok, token.Food):
                Arc.store_food(tok)
        self._tokens = []

    def to_dict(self):
        data = {'type': 'foodcourt', 'worker': None, 'food': 0}
        for tok in self._tokens:
            if isinstance(tok, token.Food):
                data['food'] += 1
            else:
                data['worker'] = tok.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        foodcourt = cls()
        if data['worker']:
            worker = token.Worker.from_dict(data['worker'])
            foodcourt._add_token(worker)

        for _ in range(data['food']):
            food = token.Food()
            foodcourt._add_token(food)
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
                'mode': self._mode.value
                }
        for tok in self._tokens:
            if isinstance(tok, token.Product):
                data['products'] += 1
            else:
                data['workers'].append(tok.to_dict())
        return data

    @classmethod
    def from_dict(cls, data):
        apartment = cls()
        for worker in data['workers']:
            worker = token.Worker.from_dict(worker)
            apartment._add_token(worker)

        for _ in range(data['products']):
            product = token.Product()
            apartment._add_token(product)

        apartment._mode = ApartmentMode(data['mode'])
        return apartment


class Farmland(Transition):
    risk = 0.5
    health_decrease = 40
    production_time = 1

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        parameters = {'lable': 'Farmland', 'color': '#9C7200'}
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)

    def _get_tokens(self):
        if not self._find_token(token.Worker):
        worker = Arc.get_worker()
            if worker:
        self._add_token(worker)
        return bool(self._find_token(token.Worker))

    def _trigger(self):
        sleep(Farmland.production_time)
        food = token.Food()
        self._add_token(food)
        if random.random() < Farmland.risk:
            self._find_token(token.Worker).decrease_health(
                Farmland.health_decrease)

    def _release_tokens(self):
        sleep(Arc.transport_time)
        for tok in self._tokens:
            self._gui_component.remove_token(tok.get_gui_component)
            if isinstance(tok, token.Worker):
                Arc.store_worker(tok)
            elif isinstance(tok, token.Food):
                Arc.store_food(tok)
        self._tokens = []

    def to_dict(self):
        data = {'type': 'farmland', 'worker': None, 'food': 0}
        for tok in self._tokens:
            if isinstance(tok, token.Food):
                data['food'] += 1
            else:
                data['worker'] = tok.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        farmland = cls()
        if data['worker']:
            worker = token.Worker.from_dict(data['worker'])
            farmland._add_token(worker)

        for _ in range(data['food']):
            food = token.Food()
            farmland._add_token(food)
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
        for tok in self._tokens:
            if isinstance(tok, token.Product):
                data['products'] += 1
            else:
                data['worker'] = tok.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        factory = cls()
        if data['worker']:
            worker = token.Worker.from_dict(data['worker'])
            factory._add_token(worker)

        for _ in range(data['products']):
            product = token.Product()
            factory._add_token(product)
        return factory


@unique
class ApartmentMode(Enum):
    NEUTRAL = 1
    REST = 2
    MULTIPLY = 3
