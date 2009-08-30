#!/usr/bin/env python

"""
jef2svg.py - Converts the contents of JEF files to SVG images.

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

import os, struct, sys
from PyQt4.QtCore import QRect, QT_VERSION
from PyQt4.QtGui import *
from PyQt4.QtSvg import QSvgGenerator

import jef

class Convertor:

    def __init__(self, path):
    
        self.jef = jef.Pattern(path)
    
    def bounding_rect(self):
    
        x, y = [], []
        for coordinates in self.jef.coordinates:
            x.extend(map(lambda (op, i, j): i, coordinates))
            y.extend(map(lambda (op, i, j): j, coordinates))
        
        return QRect(min(x), -max(y), max(x) - min(x), max(y) - min(y))
    
    def show(self, painter):
    
        i = 0
        for i in range(self.jef.threads):
        
            colour = QColor(*self.jef.colour_for_thread(i))
            coordinates = self.jef.coordinates[i]
            
            pen = QPen(QColor(200, 200, 200))
            painter.setPen(pen)
            
            for op, x, y in coordinates:
                painter.drawEllipse(x - 2, -y - 2, 4, 4)
            
            pen = QPen(colour)
            painter.setPen(pen)
            
            mx, my = 0, 0
            for op, x, y in coordinates:
                if op == "stitch":
                    painter.drawLine(mx, -my, x, -y)
                mx, my = x, y
            
            i += 1


if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s <JEF file> <SVG file>\n" % sys.argv[0])
        sys.exit(1)
    
    app = QApplication(sys.argv)
    svg = QSvgGenerator()
    svg.setFileName(sys.argv[2])
    
    if QT_VERSION >= (4, 5, 0):
        svg.setDescription(
            'Original JEF file "' + os.path.split(sys.argv[1])[1] + '" converted '
            'to ' + os.path.split(sys.argv[2])[1] + ' by jef2svg.py.'
            )
    
    convertor = Convertor(sys.argv[1])
    rect = convertor.bounding_rect()
    svg.setViewBox(rect)
    svg.setSize(rect.size())
    
    painter = QPainter()
    painter.begin(svg)
    convertor.show(painter)
    painter.end()
    
    sys.exit()
