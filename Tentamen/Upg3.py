import math


class Ball:
    """Ball class."""

    def __init__(self, radius):
        """Initialize ball."""
        self._radius = radius
        self._volume = self._calc_volume()

    @property
    def radius(self):
        """Return the radius of the ball."""
        return self._radius

    @property
    def volume(self):
        """Return the volume of the ball."""
        return self._volume

    def _calc_volume(self):
        """Calculate the volume of the ball, assuming it's a 3D sphere."""
        return 4/3*math.pi*self._radius**3

    def __eq__(self, other):
        """Test if two balls have the same radius."""
        return self.radius == other.radius

    def __ge__(self, other):
        """Test if owns radius is greater than or equal to other's radius."""
        return self.radius >= other.radius

    def __le__(self, other):
        """Test if owns radius is less than or equal to other's radius."""
        return self.radius <= other.radius

    def __gt__(self, other):
        """Test if owns radius is greater than other's radius."""
        return self.radius > other.radius

    def __lt__(self, other):
        """Test if owns radius is less than other's radius."""
        return self.radius < other.radius


if __name__ == "__main__":
    ball1 = Ball(5)
    ball2 = Ball(4)
    ball3 = Ball(5)
    print(ball1.volume)
    print(ball1 < ball2)
    print(ball1 > ball2)
    print(ball1 == ball2)
    print(ball1 == ball3)
