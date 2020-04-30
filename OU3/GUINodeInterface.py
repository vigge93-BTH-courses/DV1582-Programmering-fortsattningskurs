import simulation
from threading import Lock


class GUINodeInterface():
    '''Abstract class for GUINodeComponent implementation.'''

    def __init__(self):
        self._gui_component = None

        self._lock = Lock()

    def __del__(self):
        self._lock.acquire()
        simulation.Simulation.gui.remove(self._gui_component)
        self._lock.release()

    def lock(self):
        self._lock.acquire()

    def release(self):
        self._lock.release()

    @property
    def get_gui_component(self):
        '''Returns the GUINodeComponent.'''
        return self._gui_component

    def remove_gui_component(self):
        '''Removes gui component from gui.'''
        self._lock.acquire()
        if self._gui_component:
            simulation.Simulation.gui.remove(self.get_gui_component)
        self._lock.release()

    def create_gui_component(self):
        raise NotImplementedError
