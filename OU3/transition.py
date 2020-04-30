from enum import Enum, unique
import random
from time import sleep
from threading import Thread

import simulation
import token_simsims as token
from gui_node_interface import GUINodeInterface
from arc import Arc


class Transition(GUINodeInterface, Thread):
    """Parent class for all transitions."""

    def __init__(self):
        Thread.__init__(self)
        GUINodeInterface.__init__(self)
        self._tokens = []
        self._stop_thread = False

    def run(self):
        """Runs the thread."""
        while not self._stop_thread:
            if self._get_tokens():
                self._trigger()
                self._release_tokens()
            else:
                sleep(2)
        self._release_tokens()
        print('Thread closed')

    def finish_thread(self):
        """Sets a flag for the thread to finish."""
        self._stop_thread = True

    def _add_token(self, token_, /):
        """Appends a token to the tokens and adds it to the gui."""
        self.lock()
        token_.lock()
        self._gui_component.add_token(token_.get_gui_component)
        self._tokens.append(token_)
        self.release()
        token_.release()

    def _remove_token(self, token_, /):
        """Removes a token and it's gui component."""
        self.lock()
        token_.lock()
        self._gui_component.remove_token(token_.get_gui_component)
        self._tokens.remove(token_)
        self.release()
        token_.release()

    def _get_tokens(self):
        raise NotImplementedError

    def _find_token(self, type_, /):
        """Returns the first token of type type_. Returns None if no token is found."""
        for token_ in self._tokens:
            if isinstance(token_, type_):
                return token_
        return None

    def _trigger(self):
        raise NotImplementedError

    def _release_tokens(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(self, data):
        raise NotImplementedError


class Foodcourt(Transition):
    """Foodcourt type transition. Heals workers and consumes food."""
    poisoning_risk = 0.01
    min_restore = 40
    max_restore = 70
    production_time = 0.5

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        """Creates a green transition gui component."""
        parameters = {'lable': 'Foodcourt', 'color': '#00FF00'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)
        simulation.Simulation.lock.release()
        self.release()

    def _get_tokens(self):
        """Fetches one worker and one food."""
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
        """Consumes one food and heals or poisons worker."""
        sleep(Foodcourt.production_time)

        health_diff = random.randint(
            Foodcourt.min_restore, Foodcourt.max_restore)

        if random.random() < Foodcourt.poisoning_risk:
            self._find_token(token.Worker).decrease_health(health_diff)
        else:
            self._find_token(token.Worker).increase_health(health_diff//5)

        self._remove_token(self._find_token(token.Food))

    def _release_tokens(self):
        """Returns tokens to their places."""
        for token_ in self._tokens:
            self.lock()
            token_.lock()
            self._gui_component.remove_token(token_.get_gui_component)
            token_.release()
            self.release()
            if isinstance(token_, token.Worker):
                Arc.store_worker(token_)
            elif isinstance(token_, token.Food):
                Arc.store_food(token_)
        self._tokens = []

    def to_dict(self):
        """Serializes foodcourt to a dictionary."""
        data = {
            'type': 'foodcourt',
            'worker': None,
            'food': 0,
        }
        for token_ in self._tokens:
            if isinstance(token_, token.Food):
                data['food'] += 1
            else:
                data['worker'] = token_.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a foodcourt from a dicitonary."""
        foodcourt = cls()
        if data['worker']:
            foodcourt._add_token(token.Worker.from_dict(data['worker']))

        for _ in range(data['food']):
            foodcourt._add_token(token.Food())
        return foodcourt


class Apartment(Transition):
    """Apartment type transition. Heals or creates workers and consumes products."""
    health_restore = 20
    rest_time = 0.7

    def __init__(self):
        super().__init__()
        self.create_gui_component()
        self._mode = ApartmentMode.NEUTRAL

    @property
    def get_mode(self):
        """Returns current mode of apartment."""
        return self._mode

    def create_gui_component(self):
        """Creates a black transition gui component."""
        parameters = {'lable': 'Apartment', 'color': '#000000'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)
        simulation.Simulation.lock.release()
        self.release()

    def set_mode(self, mode):
        """Sets the mode of the apartment."""
        self._mode = mode

    def _get_tokens(self):
        """Fetches one product and one or two workers."""
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
        """If apartment has one worker, heal it. If apartment has two workers, create a third worker. Consumes the product."""
        sleep(Apartment.rest_time)
        if len(self._tokens) == 3:
            self._add_token(token.Worker())
        else:
            self._find_token(token.Worker).increase_health(
                Apartment.health_restore)

        self._remove_token(self._find_token(token.Product))

    def _release_tokens(self):
        """Returns all tokens to their places."""
        for token_ in self._tokens:
            token_.lock()
            self.lock()
            self._gui_component.remove_token(token_.get_gui_component)
            self.release()
            token_.release()
            if isinstance(token_, token.Worker):
                Arc.store_worker(token_)
            elif isinstance(token_, token.Product):
                Arc.store_product(token_)
        self._tokens = []

    def to_dict(self):
        """Serializes apartment to a dictionary."""
        data = {'type': 'apartment',
                'workers': [],
                'products': 0,
                'mode': self._mode.value,
                }
        for token_ in self._tokens:
            if isinstance(token_, token.Product):
                data['products'] += 1
            else:
                data['workers'].append(token_.to_dict())
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates an apartment from a dictionary."""
        apartment = cls()
        for worker in data['workers']:
            apartment._add_token(token.Worker.from_dict(worker))

        for _ in range(data['products']):
            apartment._add_token(token.Product())

        apartment._mode = ApartmentMode(data['mode'])
        return apartment


class Farmland(Transition):
    """Farmland type transition. Produces food."""
    risk = 0.05
    health_decrease = 20
    production_time = 1

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        """Creates a brown transition gui component."""
        parameters = {'lable': 'Farmland', 'color': '#9C7200'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)
        simulation.Simulation.lock.release()
        self.release()

    def _get_tokens(self):
        """Fetches a worker."""
        if not self._find_token(token.Worker):
            worker = Arc.get_worker()
            if worker:
                self._add_token(worker)
        return bool(self._find_token(token.Worker))

    def _trigger(self):
        """Produces one food and has a risk of damaging the worker."""
        sleep(Farmland.production_time)
        food = token.Food()
        self._add_token(food)
        if random.random() < Farmland.risk:
            self._find_token(token.Worker).decrease_health(
                Farmland.health_decrease)

    def _release_tokens(self):
        """Returns all tokens to their places"""
        for token_ in self._tokens:
            self.lock()
            token_.lock()
            self._gui_component.remove_token(token_.get_gui_component)
            token_.release()
            self.release()
            if isinstance(token_, token.Worker):
                Arc.store_worker(token_)
            elif isinstance(token_, token.Food):
                Arc.store_food(token_)
        self._tokens = []

    def to_dict(self):
        """Serializes farmland to a dictionary."""
        data = {
            'type': 'farmland',
            'worker': None,
            'food': 0,
        }
        for token_ in self._tokens:
            if isinstance(token_, token.Food):
                data['food'] += 1
            else:
                data['worker'] = token_.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a farmland from a dictionary."""
        farmland = cls()
        if data['worker']:
            farmland._add_token(token.Worker.from_dict(data['worker']))

        for _ in range(data['food']):
            farmland._add_token(token.Food())
        return farmland


class Factory(Transition):
    """Factory type transition. Produces products."""
    base_production_time = 1
    production_time_multiplier = 0.02
    death_rate = 0.01
    min_damage = 5
    max_damage = 15

    def __init__(self):
        super().__init__()
        self.create_gui_component()

    def create_gui_component(self):
        """Creates a red transition gui component."""
        parameters = {'lable': 'Factory', 'color': '#ADADAD'}
        self.lock()
        simulation.Simulation.lock.acquire()
        self._gui_component = simulation.Simulation.gui.create_transition_ui(
            parameters)
        simulation.Simulation.lock.release()
        self.release()

    def _get_tokens(self):
        """Fetches a worker."""
        if not self._find_token(token.Worker):
            worker = Arc.get_worker()
            if worker:
                self._add_token(worker)
        return bool(self._find_token(token.Worker))

    def _trigger(self):
        """Produces one product. Production time depends on workers health.
        Reduces worker's health and has a small risk of killing it.
        """
        worker = self._find_token(token.Worker)
        production_time = (Factory.base_production_time
                           + (token.Worker.max_health - worker.health)
                           * Factory.production_time_multiplier)
        sleep(production_time)
        self._add_token(token.Product())
        worker.decrease_health(random.randint(
            Factory.min_damage, Factory.max_damage))
        if random.random() < Factory.death_rate:
            self._remove_token(worker)

    def _release_tokens(self):
        """Returns tokens to their places."""
        for token_ in self._tokens:
            self.lock()
            token_.lock()
            self._gui_component.remove_token(token_.get_gui_component)
            token_.release()
            self.release()
            if isinstance(token_, token.Worker):
                Arc.store_worker(token_)
            elif isinstance(token_, token.Product):
                Arc.store_product(token_)
        self._tokens = []

    def to_dict(self):
        """Serializes factory to a dictionary."""
        data = {
            'type': 'factory',
            'worker': None,
            'products': 0,
        }
        for token_ in self._tokens:
            if isinstance(token_, token.Product):
                data['products'] += 1
            else:
                data['worker'] = token_.to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        factory = cls()
        if data['worker']:
            factory._add_token(token.Worker.from_dict(data['worker']))

        for _ in range(data['products']):
            factory._add_token(token.Product())
        return factory


@unique
class ApartmentMode(Enum):
    NEUTRAL = 1
    REST = 2
    MULTIPLY = 3
