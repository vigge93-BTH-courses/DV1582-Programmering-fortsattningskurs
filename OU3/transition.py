"""Module for transitions."""
import random
from enum import Enum, unique
from threading import Event, Thread

import token_simsims as token
from gui_node_interface import GUINodeInterface


class Transition(GUINodeInterface, Thread):
    """Parent class for all transitions."""

    def __init__(self, gui, arc):
        """Initialize transition."""
        Thread.__init__(self)
        GUINodeInterface.__init__(self, gui)

        self._tokens = []
        self._arc = arc
        self._stop_thread = False
        self._timer = Event()

    def run(self):
        """Run the thread."""
        while not self._stop_thread:
            if self._get_tokens():
                self._trigger()
                self._release_tokens()
            else:
                self._timer.wait(2)
        self._release_tokens()
        print('Thread closed')

    def finish_thread(self):
        """Set a flag for the thread to finish."""
        self._stop_thread = True
        self._timer.set()

    def _add_token(self, token_):
        """Append a token to the tokens and add it to the gui."""
        self.lock()
        token_.lock()
        self._gui_component.add_token(token_.get_gui_component)
        self._tokens.append(token_)
        self.release()
        token_.release()

    def _remove_token(self, token_):
        """Remove a token and it's gui component."""
        self.lock()
        token_.lock()
        self._gui_component.remove_token(token_.get_gui_component)
        self._tokens.remove(token_)
        self.release()
        token_.release()

    def _find_token(self, type_):
        """Return the first token of type type_. Return None if no token is found."""
        for token_ in self._tokens:
            if isinstance(token_, type_):
                return token_
        return None

    def _get_tokens(self):
        raise NotImplementedError

    def _trigger(self):
        raise NotImplementedError

    def _release_tokens(self):
        raise NotImplementedError

    def to_dict(self):
        """Abstract method to create a dict from a transition."""
        raise NotImplementedError

    @classmethod
    def from_dict(self, data, gui, arc):
        """Abstract method to create transition from a dict."""
        raise NotImplementedError


class Foodcourt(Transition):
    """Foodcourt type transition. Heals workers and consumes food."""

    poisoning_risk = 0.01
    min_restore = 40
    max_restore = 70
    production_time = 0.5

    def __init__(self, gui, arc):
        """Initialize foodcourt."""
        super().__init__(gui, arc)

    def _create_gui_component(self):
        """Create a green transition gui component."""
        parameters = {'lable': 'Foodcourt', 'color': '#00FF00'}
        self.lock()
        self._gui_component = self._gui.create_transition_ui(parameters)
        self.release()

    def _get_tokens(self):
        """Fetch one worker and one food."""
        if not self._find_token(token.Worker):
            if worker := self._arc.get_worker():
                self._add_token(worker)
        if not self._find_token(token.Food):
            if food := self._arc.get_food():
                self._add_token(food)
        return self._find_token(token.Worker) and self._find_token(token.Food)

    def _trigger(self):
        """Consume one food and heal or poison worker."""
        self._timer.wait(Foodcourt.production_time)

        health_diff = random.randint(
            Foodcourt.min_restore, Foodcourt.max_restore)

        if random.random() < Foodcourt.poisoning_risk:
            self._find_token(token.Worker).decrease_health(health_diff)
        else:
            self._find_token(token.Worker).increase_health(health_diff//5)

        self._remove_token(self._find_token(token.Food))

    def _release_tokens(self):
        """Return tokens to their places."""
        for token_ in self._tokens:
            self.lock()
            token_.lock()
            self._gui_component.remove_token(token_.get_gui_component)
            token_.release()
            self.release()
            if isinstance(token_, token.Worker):
                self._arc.store_worker(token_)
            elif isinstance(token_, token.Food):
                self._arc.store_food(token_)
        self._tokens = []

    def to_dict(self):
        """Serialize foodcourt to a dictionary."""
        data = {
            'type': 'foodcourt',
            'worker': None,
            'food': 0,
        }
        for token_ in self._tokens:
            if isinstance(token_, token.Food):
                data['food'] += 1
            elif token_.get_health > 0:
                data['worker'] = token_.to_dict()
        return data

    @classmethod
    def from_dict(cls, data, gui, arc):
        """Create a foodcourt from a dicitonary."""
        foodcourt = cls(gui, arc)
        if data['worker']:
            foodcourt._add_token(token.Worker.from_dict(data['worker'], gui))

        for _ in range(data['food']):
            foodcourt._add_token(token.Food(gui))
        return foodcourt


class Apartment(Transition):
    """Apartment type transition. Heals or creates workers and consumes products."""

    health_restore = 20
    rest_time = 0.7

    def __init__(self, gui, arc):
        """Initialize apartment."""
        super().__init__(gui, arc)
        self._mode = ApartmentMode.NEUTRAL

    @property
    def get_mode(self):
        """Return current mode of apartment."""
        return self._mode

    def set_mode(self, mode):
        """Set the mode of the apartment."""
        self._mode = mode

    def _create_gui_component(self):
        """Create a black transition gui component."""
        parameters = {'lable': 'Apartment', 'color': '#000000'}
        self.lock()
        self._gui_component = self._gui.create_transition_ui(parameters)
        self.release()

    def _get_tokens(self):
        """Fetch one product and one or two workers."""
        if not self._find_token(token.Product):
            if product := self._arc.get_product():
                self._add_token(product)
        if not self._find_token(token.Worker):
            if worker := self._arc.get_worker():
                self._add_token(worker)
            if ((self._mode == ApartmentMode.NEUTRAL and random.random() < 0.5)
                    or self._mode == ApartmentMode.MULTIPLY):
                if worker := self._arc.get_worker():
                    self._add_token(worker)
        return (self._find_token(token.Product)
                and self._find_token(token.Worker))

    def _trigger(self):
        """If apartment has one worker, heal it. If apartment has two workers, create a third worker. Consumes the product."""
        self._timer.wait(Apartment.rest_time)
        if len(self._tokens) == 3:  # Two workers and one product
            self._add_token(token.Worker(self._gui))
        else:
            self._find_token(token.Worker).increase_health(
                Apartment.health_restore)

        self._remove_token(self._find_token(token.Product))

    def _release_tokens(self):
        """Return all tokens to their places."""
        for token_ in self._tokens:
            token_.lock()
            self.lock()
            self._gui_component.remove_token(token_.get_gui_component)
            self.release()
            token_.release()
            if isinstance(token_, token.Worker):
                self._arc.store_worker(token_)
            elif isinstance(token_, token.Product):
                self._arc.store_product(token_)
        self._tokens = []

    def to_dict(self):
        """Serialize apartment to a dictionary."""
        data = {'type': 'apartment',
                'workers': [],
                'products': 0,
                'mode': self._mode.value,
                }
        for token_ in self._tokens:
            if isinstance(token_, token.Product):
                data['products'] += 1
            elif token_.get_health > 0:
                data['workers'].append(token_.to_dict())
        return data

    @classmethod
    def from_dict(cls, data, gui, arc):
        """Create an apartment from a dictionary."""
        apartment = cls(gui, arc)
        for worker in data['workers']:
            apartment._add_token(token.Worker.from_dict(worker, gui))

        for _ in range(data['products']):
            apartment._add_token(token.Product(gui))

        apartment._mode = ApartmentMode(data['mode'])
        return apartment


class Farmland(Transition):
    """Farmland type transition. Produces food."""

    risk = 0.05
    health_decrease = 20
    production_time = 1

    def __init__(self, gui, arc):
        """Initialize farmland."""
        super().__init__(gui, arc)

    def _create_gui_component(self):
        """Create a brown transition gui component."""
        parameters = {'lable': 'Farmland', 'color': '#9C7200'}
        self.lock()
        self._gui_component = self._gui.create_transition_ui(parameters)
        self.release()

    def _get_tokens(self):
        """Fetch a worker."""
        if not self._find_token(token.Worker):
            if worker := self._arc.get_worker():
                self._add_token(worker)
        return bool(self._find_token(token.Worker))

    def _trigger(self):
        """Produce one food, has a risk of damaging the worker."""
        self._timer.wait(Farmland.production_time)
        food = token.Food(self._gui)
        self._add_token(food)
        if random.random() < Farmland.risk:
            self._find_token(token.Worker).decrease_health(
                Farmland.health_decrease)

    def _release_tokens(self):
        """Return all tokens to their places."""
        for token_ in self._tokens:
            self.lock()
            token_.lock()
            self._gui_component.remove_token(token_.get_gui_component)
            token_.release()
            self.release()
            if isinstance(token_, token.Worker):
                self._arc.store_worker(token_)
            elif isinstance(token_, token.Food):
                self._arc.store_food(token_)
        self._tokens = []

    def to_dict(self):
        """Serialize farmland to a dictionary."""
        data = {
            'type': 'farmland',
            'worker': None,
            'food': 0,
        }
        for token_ in self._tokens:
            if isinstance(token_, token.Food):
                data['food'] += 1
            elif token_.get_health > 0:
                data['worker'] = token_.to_dict()
        return data

    @classmethod
    def from_dict(cls, data, gui, arc):
        """Create a farmland from a dictionary."""
        farmland = cls(gui, arc)
        if data['worker']:
            farmland._add_token(token.Worker.from_dict(data['worker'], gui))

        for _ in range(data['food']):
            farmland._add_token(token.Food(gui))
        return farmland


class Factory(Transition):
    """Factory type transition. Produces products."""

    base_production_time = 1
    production_time_multiplier = 0.02
    death_rate = 0.01
    min_damage = 5
    max_damage = 15

    def __init__(self, gui, arc):
        """Inititalize factory."""
        super().__init__(gui, arc)

    def _create_gui_component(self):
        """Create a red transition gui component."""
        parameters = {'lable': 'Factory', 'color': '#6666ff'}
        self.lock()
        self._gui_component = self._gui.create_transition_ui(parameters)
        self.release()

    def _get_tokens(self):
        """Fetch a worker."""
        if not self._find_token(token.Worker):
            if worker := self._arc.get_worker():
                self._add_token(worker)
        return bool(self._find_token(token.Worker))

    def _trigger(self):
        """Produce one product. Production time depends on workers health.

        Reduces worker's health and has a small risk of killing it.
        """
        worker = self._find_token(token.Worker)
        production_time = (Factory.base_production_time
                           + (token.Worker.max_health - worker.health)
                           * Factory.production_time_multiplier)
        self._timer.wait(production_time)
        self._add_token(token.Product(self._gui))
        worker.decrease_health(random.randint(
            Factory.min_damage, Factory.max_damage))
        if random.random() < Factory.death_rate:
            self._remove_token(worker)

    def _release_tokens(self):
        """Return tokens to their places."""
        for token_ in self._tokens:
            self.lock()
            token_.lock()
            self._gui_component.remove_token(token_.get_gui_component)
            token_.release()
            self.release()
            if isinstance(token_, token.Worker):
                self._arc.store_worker(token_)
            elif isinstance(token_, token.Product):
                self._arc.store_product(token_)
        self._tokens = []

    def to_dict(self):
        """Serialize factory to a dictionary."""
        data = {
            'type': 'factory',
            'worker': None,
            'products': 0,
        }
        for token_ in self._tokens:
            if isinstance(token_, token.Product):
                data['products'] += 1
            elif token_.get_health > 0:
                data['worker'] = token_.to_dict()
        return data

    @classmethod
    def from_dict(cls, data, gui, arc):
        """Create a factory from a dictionary."""
        factory = cls(gui, arc)
        if data['worker']:
            factory._add_token(token.Worker.from_dict(data['worker'], gui))

        for _ in range(data['products']):
            factory._add_token(token.Product(gui))
        return factory


@unique
class ApartmentMode(Enum):
    """Enum for apartment modes."""

    NEUTRAL = 1
    REST = 2
    MULTIPLY = 3
