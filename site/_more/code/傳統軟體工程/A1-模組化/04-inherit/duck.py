class Dog:
    def say(self):
        return "汪汪..."

class Cat:
    def say(self):
        return "喵喵..."

class People:
    def say(self):
        return "你好..."

zoo = [Cat(), Dog(), People()]
for animal in zoo:
    print(animal.say())
