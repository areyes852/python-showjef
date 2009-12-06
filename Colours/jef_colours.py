#!/usr/bin/env python

import sys

import all_colours
import janome_colours
import robison_rayon_colours
import robison_polyester_colours
import sulky_rayon_colours
import measured_colours
import internal_colours

known_colours = all_colours.groups
known_colours.update(janome_colours.groups)
known_colours.update(robison_rayon_colours.groups)
known_colours.update(robison_polyester_colours.groups)
known_colours.update(sulky_rayon_colours.groups)

colours = {}
colour_mappings = {}

# Examine the dictionaries mapping internal colour codes to other colour codes,
# looking up each code in the dictionaries mapping colour codes to known
# colours.

for group in internal_colours.order:

    if known_colours.has_key(group):
    
        colours_dict = known_colours[group]
        
        for internal_code, other_code in internal_colours.groups[group].items():
        
            if not colours_dict.has_key(other_code):
                continue
            
            colour_mappings.setdefault(internal_code, {})[group] = other_code
            
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
