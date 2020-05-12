from random import random
from time import perf_counter, sleep
from threading import Thread, Event


class Competitor(Thread):
    def __init__(self, name):
        Thread.__init__(self)
        self._name = name      # Name of the self
        self._points = 0.0    # Competing as long as > 0.0
        self._penelty_time = 1.0
        self._timer = Event()

    @property
    def name(self):
        return self._name

    @property
    def points(self):
        return self._points

    @property
    def competing(self):
        """True if the self is still competing."""
        return self._points > 0.0

    @competing.setter
    def competing(self, b):
        """Set as True to start competing and False to stop competing."""
        if b and (self._points == 0.0):
            self._points = 100.0
        if not b:
            self._points = 0.0
            self._timer.set()  # Quit waiting

    def run(self):
        self.competing = True
        print(f"{self.name} has started")
        while self.competing:
            self.turn()
            print("{} has {:.2f} points".format(self.name, self.points))
            if self.competing:
                self.rest()
            else:
                print(f"{self.name} har quit")

    def turn(self):
        """Update points and time to rest."""
        score = 20.0*random() - 15.0
        # Update points
        self._points = max(0.0, self._points + score)
        self._penelety_time = 1.0 + 0.05 * score

    def rest(self):
        """Rests."""
        self._timer.wait(self._penelty_time)


if __name__ == "__main__":
    competitors = [Competitor("Ingemar"),
                   Competitor("Magdalena"),
                   Competitor("Danijela")]

    for c in competitors:
        # All self's score are set to 100
        c.start()

    for c in competitors:
        c.join()

    print("The competition has ended.")
