#!/usr/bin/env python

"""
jef.py - Read and write JEF files.

Copyright (C) 2009 David Boddie <david@boddie.org.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import struct, sys, time

from Colours import jef_colours

class Pattern:

    def __init__(self, path):
    
        d = open(path).read()
        start = struct.unpack("<I", d[:4])[0]
        data = d[start:]
        self.threads = struct.unpack("<I", d[24:28])[0]
        data_length = struct.unpack("<I", d[28:32])[0]
        
        # start + data_length should equal the file length.
        
        flags = struct.unpack("<I", d[32:36])[0]
        
        # These are the width and height of the pattern. Information appears
        # to be duplicated in most patterns, though sometimes there are
        # differences of 1 unit between widths or heights.
        
        width1 = struct.unpack("<I", d[36:40])[0]
        height1 = struct.unpack("<I", d[40:44])[0]
        width2 = struct.unpack("<I", d[44:48])[0]
        height2 = struct.unpack("<I", d[48:52])[0]
        
        if flags & 1 == 0:
            # The 4 byte words from 68 to 74 should all be -1.
            pass
        
        self.date_time = None
        if struct.unpack("<I", d[4:8])[0] & 1:
            self.date_time = time.strptime(d[8:22], "%Y%m%d%H%M%S")
        
        # The colour table always seems to start at offset 0x74.
        self.colours = []
        colours = (start - 0x74)/8
        offset = 0x74
        for i in range(colours):
            self.colours.append(struct.unpack("<i", d[offset:offset+4])[0])
            offset += 4
        
        self.read_threads(data)
    
    def read_threads(self, data):
    
        self.coordinates = []
        x, y = 0, 0
        
        coordinates = []
        first = True
        i = 0
        
        while i < len(data):
        
            if data[i:i+2] == "\x80\x01":
                # Starting a new thread. Record the coordinates already read
                # and skip the next two bytes.
                self.coordinates.append(coordinates)
                coordinates = []
                first = True
                i += 4
                continue
            elif data[i:i+2] == "\x80\x02":
                # Move command.
                i += 2
                command = "move"
                first = True
            elif data[i:i+2] == "\x80\x10":
                # End of data.
                self.coordinates.append(coordinates)
                break
            else:
                command = "stitch"
            
            x += struct.unpack("<b", data[i])[0]
            y += struct.unpack("<b", data[i+1])[0]
            
            if command == "move":
                coordinates.append((command, x, y))
            elif first:
                coordinates.append(("move", x, y))
                first = False
            else:
                coordinates.append((command, x, y))
            
            i += 2
    
    def colour_for_thread(self, index):
    
        try:
            identifier = self.colours[index]
            colour = jef_colours.colour(identifier)
        except KeyError:
            colour = (0, 0, 0)
            sys.stderr.write("Thread %i: Failed to find colour 0x%02x (%i).\n" % (index, identifier, identifier))
        
        return colour
