class Recipe:
    def __init__(self, ingredients, duration, quantity, made_in, prod_allowed=False):
        self.ingredients = ingredients
        self.duration = duration
        self.quantity = quantity
        self.made_in = made_in
        self.prod_allowed = prod_allowed
