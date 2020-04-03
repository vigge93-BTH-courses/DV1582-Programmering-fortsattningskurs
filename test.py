class Pet:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("You need to define a speak method!")


class Dog(Pet):
    def __init__(self, name):
        Pet.__init__(self, name)
        self.bitten_mailmans = 0

    def speak(self):
        return "Woof!"


class Cat(Pet):
    def __init__(A):
        self.mice_catched = 0


if __name__ == "__main__":
    mypet = Dog("Smokey")
    print(mypet.name)
    print(mypet.speak())
