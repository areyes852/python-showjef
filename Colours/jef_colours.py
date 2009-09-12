#!/usr/bin/env python

import sys

import all_colours
import measured_colours
import internal_colours

known_colours = all_colours.groups

colours = {}

# Examine the dictionaries mapping internal colour codes to other colour codes,
# looking up each code in the dictionaries mapping colour codes to known
# colours.

for group in internal_colours.order:

    if known_colours.has_key(group):
    
        colours_dict = known_colours[group]
        
        for internal_code, other_code in internal_colours.groups[group].items():
        
            if colours.has_key(internal_code):
                continue
            
            try:
                colours[internal_code] = colours_dict[other_code]
            except KeyError:
                pass


def colour(identifier):

    try:
        name, rgb = colours[identifier]
    except KeyError:
        name, rgb = measured_colours.colours[identifier]
    
    return int(rgb[1:3], 16), int(rgb[3:5], 16), int(rgb[5:7], 16)
