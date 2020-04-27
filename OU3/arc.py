import time
from threading import Lock


class Arc():
    # TODO Make thread safe
    '''Static class to manage transportation of tokens.'''
    sim = None
    transport_time = 0.5
    lock = Lock()

    @classmethod
    def set_simulation(cls, sim):
        '''Specify the simulation that Arc operates on.'''
        cls.sim = sim

    @classmethod
    def get_worker(cls):
        '''Gets a worker from the road. If the road is empty it returns None.'''
        while True:
            try:
                Arc.lock.acquire()
                worker = cls.sim.get_road.remove()
                Arc.lock.release()
                return worker
            except RuntimeError as err:
                Arc.lock.release()
                print(err)
                time.sleep(Arc.transport_time)

    @classmethod
    def get_food(cls):
        '''Gets a food from the shed. If the shed is empty it returns None.'''
        while True:
            try:
                Arc.lock.acquire()
                food = cls.sim.get_shed.remove()
                Arc.lock.release()
                return food
            except RuntimeError as err:
                Arc.lock.release()
                print(err)
                time.sleep(Arc.transport_time)

    @classmethod
    def get_product(cls):
        '''Gets a product from the magazine. If the magazine is empty it returns None.'''
        while True:
            try:
                Arc.lock.acquire()
                product = cls.sim.get_magazine.remove()
                Arc.lock.release()
                return product
            except RuntimeError as err:
                Arc.lock.release()
                print(err)
                time.sleep(Arc.transport_time)

    @classmethod
    def store_worker(cls, worker):
        '''Stores a worker on the road.'''
        Arc.lock.acquire()
        cls.sim.get_road.add(worker)
        Arc.lock.release()

    @classmethod
    def store_food(cls, food):
        '''Stores a food in the shed.'''
        Arc.lock.acquire()
        cls.sim.get_shed.add(food)
        Arc.lock.release()

    @classmethod
    def store_product(cls, product):
        '''Stores a product in the magazine.'''
        Arc.lock.acquire()
        cls.sim.get_magazine.add(product)
        Arc.lock.release()
