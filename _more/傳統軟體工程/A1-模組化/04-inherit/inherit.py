class Animal:
    def __init__(self, name):
        self.name = name
    def say(self):
        pass

class Dog(Animal):
    def __init__(self):
        super().__init__("dog")
    def say(self):
        return "汪汪..."

class Cat(Animal):
    def __init__(self):
        super().__init__("cat")
    def say(self):
        return "喵喵..."

class People(Animal):
    def __init__(self):
        super().__init__("people")
    def say(self):
        return "你好..."

zoo = [Cat(), Dog(), People()]
for animal in zoo:
    print(animal.name, animal.say())
