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
        pass

    @classmethod
    def from_dict(cls, data):
        pass


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
        pass

    @classmethod
    def from_dict(cls, data):
        pass


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
        pass

    @classmethod
    def from_dict(cls, data):
        pass


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
        pass

    @classmethod
    def from_dict(cls, data):
        pass


@unique
class ApartmentMode(Enum):
    NEUTRAL = auto()
    REST = auto()
    MULTIPLY = auto()
