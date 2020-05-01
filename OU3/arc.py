from time import sleep
from threading import Lock


class Arc():
    """Static class to manage transportation of tokens."""
    transport_time = 0.2

    def __init__(self, sim):
        """Specify the simulation that Arc operates on."""
        self._sim = sim
        self._lock = Lock()

    def get_worker(self):
        """Gets a worker from the road. If the road is empty, returns None."""
        sleep(Arc.transport_time)
        self._lock.acquire()
        try:
            worker = self._sim.get_road.remove()
        except RuntimeError:
            self._lock.release()
            return None
        self._lock.release()
        return worker

    def get_food(self):
        """Gets a food from the shed. If the shed is empty, returns None."""
        sleep(Arc.transport_time)
        self._lock.acquire()
        try:
            food = self._sim.get_shed.remove()
        except RuntimeError:
            self._lock.release()
            return None
        self._lock.release()
        return food

    def get_product(self):
        """Gets a product from the magazine. If the magazine is empty, returns None."""
        sleep(Arc.transport_time)
        self._lock.acquire()
        try:
            product = self._sim.get_magazine.remove()
        except RuntimeError:
            self._lock.release()
            return None
        self._lock.release()
        return product

    def store_worker(self, worker, /):
        """Stores a worker on the road."""
        sleep(Arc.transport_time)
        self._lock.acquire()
        self._sim.get_road.add(worker)
        self._lock.release()

    def store_food(self, food, /):
        """Stores a food in the shed."""
        sleep(Arc.transport_time)
        self._lock.acquire()
        self._sim.get_shed.add(food)
        self._lock.release()

    def store_product(self, product, /):
        """Stores a product in the magazine."""
        sleep(Arc.transport_time)
        self._lock.acquire()
        self._sim.get_magazine.add(product)
        self._lock.release()
