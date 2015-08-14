"""
A set of functions designed to work with colors for websites
"""
import hashlib


def string_to_hex_color(input_string):
    hashed_string = hashlib.sha1(str(input_string).encode('utf-8')).hexdigest()
    color = "#" + hashed_string[0:3].upper()

    return color
