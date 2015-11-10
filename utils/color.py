"""
A set of functions designed to work with colors and shapes for websites
"""
import hashlib


__SHAPES = ['rectangle', 'roundrectangle', 'ellipse', 'triangle',
            'hexagon', 'octagon', 'diamond', 'vee', 'rhomboid']


def string_to_hex_color(input_string):
    hashed_string = hashlib.sha1(str(input_string).encode('utf-8')).hexdigest()
    color = "#" + hashed_string[0:3].upper()

    return color


def string_to_shape(input_string):
    hashed_string = hashlib.sha1(str(input_string).encode('utf-8')).hexdigest()

    int_value = int(hashed_string[-2:].upper(), 16)
    remapped_value = round(int_value*(len(__SHAPES)-1)/255)

    return __SHAPES[remapped_value]

