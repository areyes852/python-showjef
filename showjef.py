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

import jef

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

class Convertor:

    def __init__(self, path):
    
        self.jef = jef.Pattern(path)
    
    def show_coords(self, coords, pen, scene):
    
        mx, my = 0, 0
        for op, x, y in coords:
        
            scene.addEllipse(x - 2, -y - 2, 4, 4, QPen(QColor(200,200,200)))
            
            if op == "stitch":
                scene.addLine(mx, -my, x, -y, pen)
            
            mx, my = x, y
    
    def show(self, scene):
    
        i = 0
        for thread in range(self.jef.threads):
        
            colour = QColor(*self.jef.colour_for_thread(i))
            pen = QPen(colour)
            coordinates = self.jef.coordinates[i]
            self.show_coords(coordinates, pen, scene)
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
    
    convertor = Convertor(sys.argv[1])
    convertor.show(scene)
    sys.exit(app.exec_())
