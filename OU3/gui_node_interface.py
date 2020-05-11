"""Module for implementing SimSimsGUI Nodes."""
from threading import Lock

import simulation


class GUINodeInterface():
    """Abstract class for GUINodeComponent implementation."""

    def __init__(self, gui):
        """Initialize GUINodeInterface."""
        self._gui = gui
        self._gui_component = None
        self._lock = Lock()

    def __del__(self):
        """Remove own gui_component."""
        self._lock.acquire()
        self._gui.remove(self._gui_component)
        self._lock.release()

    @property
    def get_gui_component(self):
        """Return the GUINodeComponent."""
        return self._gui_component

    def remove_gui_component(self):
        """Remove gui component from gui."""
        self._lock.acquire()
        if self._gui_component:
            self._gui.remove(self.get_gui_component)
        self._lock.release()

    def lock(self):
        """Acquire gui_component lock."""
        self._lock.acquire()

    def release(self):
        """Release gui_component lock."""
        self._lock.release()

    def _create_gui_component(self):
        """Abstract method to create gui component."""
        raise NotImplementedError
