class Arc():
    # TODO Make thread safe

    '''Static class to manage transportation of tokens.'''
    simulation = None

    @classmethod
    def set_simulation(cls, simulation):
        '''Specify the simulation that Arc operates on.'''
        cls.simulation = simulation

    @classmethod
    def get_worker(cls):
        '''Gets a worker from the road. If the road is empty it returns None.'''
        try:
            return cls.simulation.get_road.remove()
        except RuntimeError:
            return None

    @classmethod
    def get_food(cls):
        '''Gets a food from the shed. If the shed is empty it returns None.'''
        try:
            return cls.simulation.get_shed.remove()
        except RuntimeError:
            return None

    @classmethod
    def get_product(cls):
        '''Gets a product from the magazine. If the magazine is empty it returns None.'''
        try:
            return cls.simulation.get_magazine.remove()
        except RuntimeError:
            return None

    @classmethod
    def store_worker(cls, worker):
        '''Stores a worker on the road.'''
        cls.simulation.get_road.add(worker)

    @classmethod
    def store_food(cls, food):
        '''Stores a food in the shed.'''
        cls.simulation.get_shed.add(food)

    @classmethod
    def store_product(cls, product):
        '''Stores a product in the magazine.'''
        cls.simulation.get_magazine.add(product)
