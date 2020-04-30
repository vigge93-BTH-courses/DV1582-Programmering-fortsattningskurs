from time import sleep
from threading import Lock


class Arc():
    """Static class to manage transportation of tokens."""
    sim = None
    transport_time = 0.2
    lock = Lock()

    @classmethod
    def set_simulation(cls, sim, / ):
        """Specify the simulation that Arc operates on."""
        cls.sim = sim

    @classmethod
    def get_worker(cls):
        """Gets a worker from the road. If the road is empty, returns None."""
        sleep(Arc.transport_time)
        try:
            Arc.lock.acquire()
            worker = cls.sim.get_road.remove()
            Arc.lock.release()
            return worker
        except RuntimeError:
            Arc.lock.release()
            return None

    @classmethod
    def get_food(cls):
        """Gets a food from the shed. If the shed is empty, returns None."""
        sleep(Arc.transport_time)
        try:
            Arc.lock.acquire()
            food = cls.sim.get_shed.remove()
            Arc.lock.release()
            return food
        except RuntimeError:
            Arc.lock.release()
            return None

    @classmethod
    def get_product(cls):
        """Gets a product from the magazine. If the magazine is empty, returns None."""
        sleep(Arc.transport_time)
        try:
            Arc.lock.acquire()
            product = cls.sim.get_magazine.remove()
            Arc.lock.release()
            return product
        except RuntimeError:
            Arc.lock.release()
            return None

    @classmethod
    def store_worker(cls, worker, / ):
        """Stores a worker on the road."""
        sleep(Arc.transport_time)
        Arc.lock.acquire()
        cls.sim.get_road.add(worker)
        Arc.lock.release()

    @classmethod
    def store_food(cls, food, / ):
        """Stores a food in the shed."""
        sleep(Arc.transport_time)
        Arc.lock.acquire()
        cls.sim.get_shed.add(food)
        Arc.lock.release()

    @classmethod
    def store_product(cls, product, / ):
        """Stores a product in the magazine."""
        sleep(Arc.transport_time)
        Arc.lock.acquire()
        cls.sim.get_magazine.add(product)
        Arc.lock.release()
