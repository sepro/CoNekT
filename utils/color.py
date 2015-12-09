"""
A set of functions designed to work with colors and shapes for websites
"""
import hashlib


# Shapes, only those in Cytoscape.js and Cytoscape desktop are included (XGMML export)
__SHAPES = ['rectangle', 'roundrectangle', 'ellipse', 'triangle',
            'hexagon', 'octagon', 'diamond', 'vee', 'rhomboid']

# Nice colors
__COLORS = ["#993399", "#FFFF00", "#FF3300", "#7FFFD4", "#FFE4C4",
            "#D2691E", "#A9A9A9", "#00BFFF", "#FFD700", "#008000",
            "#ADFF2F", "#FF00FF"]
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

def family_to_shape_and_color(input_dictionary):
    """
    Marek
    Takes a dictionary, where key:gene ID, value: ["fam1", "fam2",...]

    :param dictionary: dictionary of genes:families
    :return: genes: [color,shape]
    """

    families = []
    for gene in input_dictionary:
        families+=[input_dictionary[gene][0][0]]

    families = list(set(families))

    fam_2_color_shape, counter = {}, 0
    if len(families)<(len(__SHAPES)*len(__COLORS)): ###pretty inefficient, will fix later
        for shape in __SHAPES:
            for color in __COLORS:
                if counter<len(families):
                    fam_2_color_shape[families[counter]] = [shape, color]
                    counter += 1

    gene_2_color_shape = {}
    for gene in input_dictionary:
        gene_2_color_shape[gene] = fam_2_color_shape[input_dictionary[gene][0][0]]

    return gene_2_color_shape
