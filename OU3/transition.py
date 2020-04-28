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
        GUINodeInterface.__init__(self)
        self._tokens = []
        self.stop_thread = False

    def run(self):
        '''Runs the thread.'''
        while not self.stop_thread:
            if self._get_tokens():
                self._trigger()
                self._release_tokens()
            else:
                sleep(2)
        self._release_tokens()
        print('thread closed')

    def finish_thread(self):
        '''Sends a signal to the thread to finish. Returns after thread is done.'''
        self.stop_thread = True

    def _add_token(self, tok, /):
        '''Appends a token to the tokens and adds it to the gui.'''
        self.lock()
        tok.lock()
        self._gui_component.add_token(tok.get_gui_component)
        self.release()
        tok.release()
        self._tokens.append(tok)

    def _remove_token(self, tok, /):
        self.lock()
        tok.lock()
        self._gui_component.remove_token(tok.get_gui_component)
        self.release()
        tok.release()
        self._tokens.remove(tok)

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

    def from_dict(self, data, /):
        raise NotImplementedError


class Foodcourt(Transition):
    poisoning_risk = 0.01
    min_restore = 40
    max_restore = 70
    production_time = 0.5

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        parameters = {'lable': 'Foodcourt', 'color': '#00FF00'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)
        simulation.Simulation.lock.release()
        self.release()

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
        for tok in self._tokens:
            self.lock()
            tok.lock()
            self._gui_component.remove_token(tok.get_gui_component)
            tok.release()
            self.release()
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
    health_restore = 20
    rest_time = 0.7

    def __init__(self):
        super().__init__()
        self.create_gui_component()
        self._mode = ApartmentMode.NEUTRAL

    @property
    def get_mode(self):
        return self._mode

    def create_gui_component(self):
        parameters = {'lable': 'Apartment', 'color': '#000000'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)
        simulation.Simulation.lock.release()
        self.release()

    def set_mode(self, mode):
        self._mode = mode

    def _get_tokens(self):
        if not self._find_token(token.Product):
            product = Arc.get_product()
            if product:
                self._add_token(product)
        if not self._find_token(token.Worker):
            worker_1 = Arc.get_worker()
            if worker_1:
                self._add_token(worker_1)
            if (self._mode == ApartmentMode.NEUTRAL and random.random() < 0.5) or self._mode == ApartmentMode.MULTIPLY:
                worker_2 = Arc.get_worker()
                if worker_2:
                    self._add_token(worker_2)
        return self._find_token(token.Product) and self._find_token(token.Worker)

    def _trigger(self):
        sleep(Apartment.rest_time)
        if len(self._tokens) == 3:
            self._add_token(token.Worker())
        else:
            self._find_token(token.Worker).increase_health(
                Apartment.health_restore)

        self._remove_token(self._find_token(token.Product))

    def _release_tokens(self):
        for tok in self._tokens:
            tok.lock()
            self.lock()
            self._gui_component.remove_token(tok.get_gui_component)
            self.release()
            tok.release()
            if isinstance(tok, token.Worker):
                Arc.store_worker(tok)
            elif isinstance(tok, token.Product):
                Arc.store_product(tok)
        self._tokens = []

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
    risk = 0.05
    health_decrease = 20
    production_time = 1

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        parameters = {'lable': 'Farmland', 'color': '#9C7200'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)
        simulation.Simulation.lock.release()
        self.release()

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
        for tok in self._tokens:
            self.lock()
            tok.lock()
            self._gui_component.remove_token(tok.get_gui_component)
            tok.release()
            self.release()
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
    base_production_time = 1
    production_time_multiplier = 0.02
    death_rate = 0.01
    min_damage = 5
    max_damage = 15

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        parameters = {'lable': 'Factory', 'color': '#ADADAD'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)
        simulation.Simulation.lock.release()
        self.release()

    def _get_tokens(self):
        if not self._find_token(token.Worker):
            worker = Arc.get_worker()
            if worker:
                self._add_token(worker)
        return bool(self._find_token(token.Worker))

    def _trigger(self):
        worker = self._find_token(token.Worker)
        production_time = Factory.base_production_time + \
            (token.Worker.max_health - worker.health) * \
            Factory.production_time_multiplier
        sleep(production_time)
        self._add_token(token.Product())
        worker.decrease_health(random.randint(
            Factory.min_damage, Factory.max_damage))
        if random.random() < Factory.death_rate:
            self._remove_token(worker)

    def _release_tokens(self):
        for tok in self._tokens:
            self.lock()
            tok.lock()
            self._gui_component.remove_token(tok.get_gui_component)
            tok.release()
            self.release()
            if isinstance(tok, token.Worker):
                Arc.store_worker(tok)
            elif isinstance(tok, token.Product):
                Arc.store_product(tok)
        self._tokens = []

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
