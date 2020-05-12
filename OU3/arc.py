"""Module for arc that handles transportation of tokens."""
from time import sleep


class Arc():
    """Static class to manage transportation of tokens."""

    transport_time = 0.2

    def __init__(self, sim):
        """Create an arc object."""
        self._sim = sim

    def get_worker(self):
        """Get a worker from the road. If the road is empty, return None."""
        sleep(Arc.transport_time)
        try:
            return self._sim.get_road.remove()
        except RuntimeError:
            return None

    def get_food(self):
        """Get a food from the shed. If the shed is empty, return None."""
        sleep(Arc.transport_time)
        try:
            return self._sim.get_shed.remove()
        except RuntimeError:
            return None

    def get_product(self):
        """Get product from the magazine. If magazine is empty, return None."""
        sleep(Arc.transport_time)
        try:
            return self._sim.get_magazine.remove()
        except RuntimeError:
            return None

    def store_worker(self, worker):
        """Store a worker on the road."""
        sleep(Arc.transport_time)
        self._sim.get_road.add(worker)

    def store_food(self, food):
        """Store a food in the shed."""
        sleep(Arc.transport_time)
        self._sim.get_shed.add(food)

    def store_product(self, product):
        """Store a product in the magazine."""
        sleep(Arc.transport_time)
        self._sim.get_magazine.add(product)
