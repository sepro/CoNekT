
def get_clade(species, clades_to_species):
    """
    Checks for a list of species which clade matches best (fewest other species in the clade).


    :param species: list of species for which the best clade needs to be determined
    :param clades_to_species: dict with clade names (keys) and lists of species (values)
    :return: tuple of the clade name
    """
    for c in sorted(clades_to_species.keys(), key=lambda k: len(clades_to_species[k])):
        cs = clades_to_species[c]
        if all([s in cs for s in species]):
            return c, cs
    else:
        return None, []


def is_duplication(set_one, set_two, clades_to_species):
    """
    Check if two sets of species are shared or not

    :param set_one:
    :param set_two:
    :param clades_to_species:
    :return:
    """
    _, species_one = get_clade(set_one, clades_to_species)
    _, species_two = get_clade(set_two, clades_to_species)

    return any([s in species_two for s in species_one])


def duplication_consistency(set_one, set_two):
    """
    Calculates the duplication consistency score for two sets of species

    :param set_one: set/list of species
    :param set_two: set/list of species
    :return: float with duplication consistency score
    """
    union_size = len(set(set_one).union(set(set_two)))
    intersection_size = len(set(set_one).intersection(set(set_two)))

    return intersection_size/union_size
