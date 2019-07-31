def get_prod_modifier(modules, prod_mod_level):
    prod_modifier = 0
    if prod_mod_level > 0:
        prod_modifier += modules["productivity_module_{}".format(prod_mod_level)].prod_modifier
    return prod_modifier


def get_totals(item_list, machines, recipes, prod_modifier, restricted_machines=[]):
    totals = {}
    while len(item_list) > 0:
        item = item_list.pop()
        item_name = item[0]
        craft_count = item[1]
        if item_name in recipes:
            recipe = recipes[item_name]
            recipe_output = recipe.quantity[0][1] * recipe.quantity[0][2] / 100
            craft_count /= recipe_output
            machine = None
            for allowed_machine in recipe.made_in:
                if allowed_machine not in restricted_machines:
                    machine = machines[allowed_machine]
                    break
            if machine:
                if recipe.prod_allowed:
                    craft_count /= 1 + machine.modules * prod_modifier
                for ingredient in recipe.ingredients:
                    item_list.append((ingredient[0], ingredient[1] * craft_count))
        if item_name not in totals:
            totals[item_name] = 0
        totals[item_name] += craft_count
    return totals


def handle_oil_processing(totals, machines, recipes, prod_modifier):
    refinery_prod_modifier = 1 + machines["oil_refinery"].modules * prod_modifier
    plant_prod_modifier = 1 + machines["chemical_plant"].modules * prod_modifier
    processing = recipes["advanced_oil_processing"]
    heavy_cracking = recipes["heavy_oil_cracking_to_light_oil"]
    light_cracking = recipes["light_oil_cracking_to_petroleum_gas"]
    refinery_crude_in = processing.ingredients[1][1]
    refinery_heavy_out = processing.quantity[0][1] * processing.quantity[0][2] / 100 * refinery_prod_modifier
    refinery_light_out = processing.quantity[1][1] * processing.quantity[1][2] / 100 * refinery_prod_modifier
    refinery_petro_out = processing.quantity[2][1] * processing.quantity[2][2] / 100 * refinery_prod_modifier
    plant_heavy_in = heavy_cracking.ingredients[1][1]
    plant_light_out = heavy_cracking.quantity[0][1] * heavy_cracking.quantity[0][2] / 100 * plant_prod_modifier
    plant_light_in = light_cracking.ingredients[1][1]
    plant_petro_out = light_cracking.quantity[0][1] * light_cracking.quantity[0][2] / 100 * plant_prod_modifier
    refinery_pure_light_out = refinery_light_out + refinery_heavy_out / plant_heavy_in * plant_light_out
    refinery_pure_petro_out = refinery_petro_out + refinery_pure_light_out / plant_light_in * plant_petro_out
    heavy_required = 0
    if "heavy_oil" in totals:
        heavy_required += totals["heavy_oil"]
    light_required = 0
    if "light_oil" in totals:
        light_required += totals["light_oil"]
    petro_required = 0
    if "petroleum_gas" in totals:
        petro_required += totals["petroleum_gas"]
    heavy_processing_required = heavy_required / refinery_heavy_out
    light_required -= heavy_processing_required * refinery_light_out
    petro_required -= heavy_processing_required * refinery_petro_out
    if light_required < 0:
        petro_required += light_required / plant_light_in * plant_petro_out
        light_required = 0
    light_processing_required = light_required / refinery_pure_light_out
    petro_required -= light_processing_required * refinery_petro_out
    if petro_required < 0:
        print("WARNING - this crafting plan produces {} excess petroleum gas and will back up if used "
              "indefinitely!".format(petro_required * -1))
        petro_required = 0
    petro_processing_required = petro_required / refinery_pure_petro_out
    processing_required = heavy_processing_required + light_processing_required + petro_processing_required
    if "crude_oil" not in totals:
        totals["crude_oil"] = 0
    totals["crude_oil"] += processing_required * refinery_crude_in


def print_totals(totals, recipes, seconds):
    print("Required crafts:")
    max_name_length = 0
    max_num_length = 0
    for item_name, craft_count in totals.items():
        item_name_length = len(item_name)
        if item_name_length > max_name_length:
            max_name_length = item_name_length
        item_num_length = len("{:.2f}".format(craft_count))
        if item_num_length > max_num_length:
            max_num_length = item_num_length
    for item_name, craft_count in sorted(totals.items()):
        padded_name = item_name + ": " + " " * (max_name_length - len(item_name))
        padded_num = "{:>{}.2f}".format(craft_count, max_num_length)
        padded_machine_units = ""
        if item_name in recipes:
            recipe = recipes[item_name]
            padded_machine_units = ", machine_units: {:.2f}".format(craft_count * recipe.duration / seconds)
        print("{}{}{}".format(padded_name, padded_num, padded_machine_units))
