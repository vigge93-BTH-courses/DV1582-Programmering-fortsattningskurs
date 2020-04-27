import simulation


class GUINodeInterface():
    '''Abstract class for GUINodeComponent implementation.'''

    def __init__(self):
        self._gui_component = None

    @property
    def get_gui_component(self):
        '''Returns the GUINodeComponent.'''
        return self._gui_component

    def remove_gui_component(self):
        '''Removes gui component from gui.'''
        if self._gui_component:
            simulation.Simulation.gui.remove(self._gui_component)

    def create_gui_component(self):
        raise NotImplementedError

    def __del__(self):
        simulation.Simulation.gui.remove(self._gui_component)
