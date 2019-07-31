from recipes.logic import *
from recipes.v0_17 import *


prod_mod_level = 3
item_list = [("science", 1000)]
seconds = 60


def main():
    machines = init_machines()
    modules = init_modules()
    recipes = init_recipes()
    prod_modifier = get_prod_modifier(modules, 3)
    totals = get_totals(item_list, machines, recipes, prod_modifier)
    handle_oil_processing(totals, machines, recipes, prod_modifier)
    print_totals(totals, recipes, seconds)


main()
