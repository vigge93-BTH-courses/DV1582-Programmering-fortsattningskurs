import p5

class Bird():
    def __init__(self):
        self._x = 60
        self._y = height/2
        self._d = 40
        self._v = 0
        self._a = 1
        self._is_dead = False

    def update(self):
        self._y += self._v
        self._v += self._a
    
    def draw(self):
        p5.fill(255)
        p5.circle((self._x, self._y), self._d)
    
    def up(self):
        self._v = -20

    def is_dead(self):
        if not 0 + self._d/2 < self._y < height - self._d/2:
            self._is_dead = True
        return self._is_dead
bird = None

def setup():
    global bird
    p5.size(700, 700)
    bird = Bird()

def draw():
    global bird
    p5.background(200)
    if not bird.is_dead():
        bird.update()
    bird.draw()

def key_pressed():
    global bird
    if key == ' ' and not bird.is_dead():
        bird.up()       

if __name__ == "__main__":
    p5.run()