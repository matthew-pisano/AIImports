
class Burger:
    def __init__(self, meat, cheese, toppings):
        self.meat = meat
        self.cheese = cheese
        self.toppings = toppings

def make_burger(meat, cheese, toppings):
    return Burger(meat, cheese, toppings)

def buy_burgers(quantity):
    burgers = [make_burger("beef", "cheddar", ["lettuce", "tomato"]) for _ in range(quantity)]
    return burgers