"""
A set of functions designed to work with colors and shapes for websites
"""
import hashlib


# Shapes, only those in Cytoscape.js and Cytoscape desktop are included (XGMML export)
__SHAPES = ['rectangle', 'roundrectangle', 'ellipse', 'triangle',
            'hexagon', 'octagon', 'diamond', 'vee', 'rhomboid']


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

