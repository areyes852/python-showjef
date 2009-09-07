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

ColorTable = {
    0x01: (0, 0, 0), # Black
    0x02: (254, 254, 254), # see table
    0x03: (249, 237, 5), # Gold Yellow
    0x05: (67, 86, 7), # see table
    0x06: (49, 125, 37), # see table
    0x08: (146, 96, 172), # see table
    0x0a: (254, 0, 0), # see table
    0x0b: (180, 78, 100), # see table
    0x0c: (35, 54, 114), # see table
    0x0d: (227, 243, 93), # see table
    0x0e: (68, 35, 4), # see table
    0x0f: (195, 189, 191), # some kind of silver (estimated)
    0x10: (255, 227, 197), # see table
    0x12: (244, 165, 132), # see table
    0x13: (184, 176, 139), # some kind of tan (estimated)
    0x14: (147, 5, 3), # see table
    0x15: (177, 176, 211), # see table
    0x17: (250, 218, 223), # see table
    0x18: (162, 162, 190), # some kind of light blue (estimated)
    0x1a: (155, 217, 235), # see table
    0x1c: (101, 154, 214), # see table
    0x1f: (196, 126, 114), # some kind of dark pink (estimated)
    0x20: (255, 0, 0),
    0x21: (133, 0, 0), # some kind of dark red (estimated)
    0x22: (201, 172, 138), # some kind of tan/skin (estimated)
    0x24: (200, 160, 0),
    0x28: (200, 0, 0),
    0x29: (78, 41, 143), # see table
    0x2b: (185, 185, 185), # some kind of grey (estimated)
    0x2c: (0, 0, 0), # black (estimated)
    0x2d: (125, 112, 2), # see table
    0x2e: (2, 56, 34), # see table
    0x32: (80, 84, 87), # see table
    0x34: (198, 98, 0), # see table
    0x35: (212, 165, 95), # see table
    0x36: (250, 127, 126), # see table
    0x37: (0, 0, 0),
    0x38: (140, 18, 55), # some kind of red (estimated)
    0x3a: (105, 45, 4), # see table
    0x3c: (0, 0, 255),
    0x3e: (158, 214, 125), # see table
    0x3f: (240, 77, 140), # see table
    0x41: (194, 47, 75), # some kind of red (estimated)
    0x43: (0, 150, 0), # see table
    0x44: (255, 240, 142), # see table
    0x45: (185, 153, 2), # see table
    0x47: (88, 156, 83), # some kind of green (estimated)
    0x48: (252, 179, 68), # see table
    0x4d: (198, 190, 194), # see table
    0x4e: (202, 156, 106), # some kind of tan/skin (estimated)
    }

class Pattern:

    def __init__(self, path):
    
        d = open(path).read()
        start = struct.unpack("<I", d[:4])[0]
        data = d[start:]
        self.threads = struct.unpack("<I", d[24:28])[0]
        data_length = struct.unpack("<I", d[28:32])[0]
        
        # start + data_length should equal the file length.
        
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
            colour = ColorTable[identifier]
        except KeyError:
            colour = (0, 0, 0)
            sys.stderr.write("Failed to find colour 0x%02x (%i).\n" % (identifier, identifier))
        
        return colour
