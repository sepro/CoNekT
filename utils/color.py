"""
A set of functions designed to work with colors and shapes for websites
"""
import hashlib
import math


# Shapes, only those in Cytoscape.js and Cytoscape desktop are included (XGMML export)
__SHAPES = ['rectangle', 'roundrectangle', 'ellipse', 'triangle',
            'hexagon', 'octagon', 'diamond', 'vee', 'rhomboid']

# Nice colors
__COLORS = ["#993399", "#FFFF00", "#FF3300", "#7FFFD4", "#FFE4C4",
            "#D2691E", "#A9A9A9", "#00BFFF", "#FFD700", "#008000",
            "#ADFF2F", "#FF00FF"]

__COLORS_RGBA = ["rgba(153, 51, 153, 0.3)", "rgba(255, 255, 0,0.3)", "rgba(255, 51, 0, 0.3)",
                 "rgba(127, 255, 212, 0.3)", "rgba(255, 228, 196, 0.3)", "rgba(210, 105, 30, 0.3)",
                 "rgba(169, 169, 169, 0.2)", "rgba(0, 191, 255,0.3)", "rgba(255, 215, 0, 0.3)",
                 "rgba(0, 128, 0, 0.3)", "rgba(173, 255, 47, 0.3)", "rgba(255, 0, 255, 0.3)"]


def string_to_hex_color(input_string):
    """
    Takes any string, generates a pseudo-random color from it. Used to generate colors for e.g. families.

    :param input_string: base string to generate a color from
    :return: a semi random color in #fff format
    """
    hashed_string = hashlib.sha1(str(input_string).encode('utf-8')).hexdigest()
    color = "#" + hashed_string[0:3].upper()

    return color


def string_to_shape(input_string):
    """
    Takes any string and returns a pseudo-randomly selected shape

    :param input_string: base string to generate the shape from
    :return: shape name
    """
    hashed_string = hashlib.sha1(str(input_string).encode('utf-8')).hexdigest()

    int_value = int(hashed_string[-2:].upper(), 16)
    remapped_value = round(int_value*(len(__SHAPES)-1)/255)

    return __SHAPES[remapped_value]


def iterative_grouper(ListOfListOfLabels, seed):
    """
    Takes a list of lists containing labels, and seed label.
    Returns label co-occurrences for the seed label
    """
    aList = []
    for i in ListOfListOfLabels:
        if len(set(i) & set(seed)) > 0:
            aList += i
    if set(aList) == set(seed):
        return set(aList) | set(seed)
    else:
        return iterative_grouper(ListOfListOfLabels, set(aList) | set(seed))


def label_coocurrence(ListOfListOfLabels):
    """
    Takes a list of lists, which contains labels associated with a gene, e.g. [[domain 1, domain 2],[domain 2, domain 3],[domain 4],...]
    Iteratively bins the labels into label co-occurrences

    :param ListOfListOfLabels: List of lists
    :return: list of label co-occurrenes: [[domain 1, domain 2, domain 3], [domain 4],...]
    """
    allFams = []
    for i in ListOfListOfLabels:
        allFams += i

    allFams = list(set(allFams))

    lc = []
    while len(allFams) > 0:
        founds = iterative_grouper(ListOfListOfLabels, [allFams[0]])
        lc.append(list(founds))
        allFams = list(set(allFams)-set(founds))

    return lc


def index_to_shape_and_color(index):
    """
    Returns a tuple (color, shape) from an index


    :param index: integer number
    :return: tuple (color, shape)
    """

    color_index = index % len(__COLORS)
    shape_index = index // len(__COLORS)
    shape_index = shape_index if shape_index < len(__SHAPES) else 0

    return __COLORS[color_index], __SHAPES[shape_index]


def family_to_shape_and_color(input_dictionary):
    """
    Takes a dictionary, where key:gene ID, value: ["fam1", "fam2",...]

    :param input_dictionary: dictionary of genes:families
    :return: genes: [color,shape]
    """
    label_co_occurrences = label_coocurrence(input_dictionary.values())

    label_to_shape_color, counter = {}, 0

    if len(label_co_occurrences) <= (len(__SHAPES)*len(__COLORS)):
        for shape in __SHAPES:
            for color in __COLORS:
                if counter < len(label_co_occurrences):
                    labels = ';'.join(map(str, label_co_occurrences[counter]))
                    for label in label_co_occurrences[counter]:
                        label_to_shape_color[label] = [shape, color, labels]
                counter += 1

    else:
        # if number of lc's is larger than product of available shapes and distinguishable colors
        for shape in __SHAPES:
            # determine how many colors per shape needs to be generated, rounded up
            for j in range(math.ceil(len(label_co_occurrences)/float(len(__SHAPES)))):
                if counter < len(label_co_occurrences):
                    hashed_string = hashlib.sha1(str(label_co_occurrences[counter][0]).encode('utf-8')).hexdigest()
                    color = "#" + hashed_string[0:3].upper()
                    labels = ';'.join(map(str, label_co_occurrences[counter]))
                    for label in label_co_occurrences[counter]:
                        label_to_shape_color[label] = [shape, color, labels]
                counter += 1

    gene_2_color_shape = {}

    for gene in input_dictionary:
        if input_dictionary[gene] != set([]):
            gene_2_color_shape[gene] = label_to_shape_color[list(input_dictionary[gene])[0]]

    return gene_2_color_shape
