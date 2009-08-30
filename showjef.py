#!/usr/bin/env python

"""
showjef.py - Display the contents of JEF files.

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

import struct, sys
from PyQt4.QtGui import *

ColorTable = {
    0x0a: QColor(255, 0, 0),
    0x3c: QColor(0, 0, 255),
    0x02: QColor(255, 255, 255),
    0x28: QColor(200, 0, 0),
    0x44: QColor(255, 240, 142),
    0x24: QColor(200, 160, 0),
    0x20: QColor(255, 0, 0),
    0x0e: QColor(0, 0, 0),
    0x37: QColor(0, 0, 0),
    0x01: QColor(0, 0, 0),
    0x0c: QColor(0, 0, 160),
    0x15: QColor(174, 176, 214),
    0x3e: QColor(159, 213, 127),
    0x0d: QColor(225, 244, 92),
    0x35: QColor(206, 166, 97),
    0x08: QColor(150, 94, 169),
    0x45: QColor(186, 153, 0),
    0x29: QColor(78, 41, 146),
    0x06: QColor(49, 125, 34),
    0x2d: QColor(128, 110, 0),
    0x05: QColor(67, 87, 2),
    0x2e: QColor(0, 57, 37),
    }

class Pattern:

    def __init__(self, path):
    
        d = open(path).read()
        start = struct.unpack("<h", d[:2])[0]
        data = d[start:]
        self.threads = map(
            lambda thread: thread[2:], data.split("\x80\x01")
            )
        self.x, self.y = 0, 0
        
        self.colours = []
        colours = (start - 0x74)/8
        offset = 0x74
        for i in range(colours):
            self.colours.append(struct.unpack("<i", d[offset:offset+4])[0])
            offset += 4
    
    def show_coords(self, coords, pen, scene):
    
        first = True
        command = False
        i = 0
        while i < len(coords):
        
            if coords[i:i+2] == "\x80\x02":
                i += 2
                command = True
                first = True
            elif coords[i:i+2] == "\x80\x10":
                break
            else:
                command = False
            
            self.x += struct.unpack("<b", coords[i])[0]
            self.y += struct.unpack("<b", coords[i+1])[0]
            
            if not command:
                if not first:
                    scene.addLine(x, -y, self.x, -self.y, pen)
                    scene.addEllipse(self.x - 2, -self.y - 2, 4, 4, QPen(QColor(200,200,200)))
                else:
                    first = False
            
            x, y = self.x, self.y
            i += 2
    
    def show(self, scene):
    
        i = 0
        for thread in self.threads:
            try:
                identifier = self.colours[i]
                colour = ColorTable[identifier]
            except KeyError:
                colour = QColor(0, 0, 0)
                sys.stderr.write("Failed to find colour 0x%02x (%i).\n" % (identifier, identifier))
            pen = QPen(colour)
            self.show_coords(thread, pen, scene)
            i += 1


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
