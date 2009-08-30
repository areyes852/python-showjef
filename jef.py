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

import struct

ColorTable = {
    0x0a: (255, 0, 0),
    0x3c: (0, 0, 255),
    0x02: (255, 255, 255),
    0x28: (200, 0, 0),
    0x44: (255, 240, 142),
    0x24: (200, 160, 0),
    0x20: (255, 0, 0),
    0x0e: (0, 0, 0),
    0x37: (0, 0, 0),
    0x01: (0, 0, 0),
    0x0c: (0, 0, 160),
    0x15: (174, 176, 214),
    0x3e: (159, 213, 127),
    0x0d: (225, 244, 92),
    0x35: (206, 166, 97),
    0x08: (150, 94, 169),
    0x45: (186, 153, 0),
    0x29: (78, 41, 146),
    0x06: (49, 125, 34),
    0x2d: (128, 110, 0),
    0x05: (67, 87, 2),
    0x2e: (0, 57, 37),
    }

class Pattern:

    def __init__(self, path):
    
        d = open(path).read()
        start = struct.unpack("<I", d[:4])[0]
        data = d[start:]
        self.threads = struct.unpack("<I", d[24:28])[0]
        
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
        self.x, self.y = 0, 0
        
        coordinates = []
        i = 0
        
        while i < len(data):
        
            if data[i:i+2] == "\x80\x01":
                # Starting a new thread. Record the coordinates already read
                # and skip the two bytes following this control code.
                self.coordinates.append(coordinates)
                coordinates = []
                i += 4
                continue
            elif data[i:i+2] == "\x80\x02":
                # Move command.
                i += 2
                command = "move"
            elif data[i:i+2] == "\x80\x10":
                # End of data.
                self.coordinates.append(coordinates)
                break
            else:
                command = "stitch"
            
            self.x += struct.unpack("<b", data[i])[0]
            self.y += struct.unpack("<b", data[i+1])[0]
            
            coordinates.append((command, self.x, self.y))
            i += 2
    
    def colour_for_thread(self, index):
    
        try:
            identifier = self.colours[index]
            colour = ColorTable[identifier]
        except KeyError:
            colour = (0, 0, 0)
            sys.stderr.write("Failed to find colour 0x%02x (%i).\n" % (identifier, identifier))
        
        return colour


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s <JEF file>\n" % sys.argv[0])
        sys.exit(1)
    
    app = QApplication(sys.argv)
    scene = QGraphicsScene()
    view = QGraphicsView()
    view.setRenderHint(QPainter.Antialiasing)
    view.setScene(scene)
    view.show()
    
    p = Pattern(sys.argv[1])
    p.show(scene)
    sys.exit(app.exec_())
