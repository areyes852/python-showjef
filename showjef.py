#!/usr/bin/env python

import struct, sys
from PyQt4.QtGui import *

ColorTable = {
    0x0a: QColor(255, 0, 0),
    0x3c: QColor(0, 0, 255),
    0x02: QColor(255, 255, 255),
    0x28: QColor(200, 0, 0),
    0x44: QColor(255, 255, 0),
    0x24: QColor(200, 160, 0),
    0x20: QColor(255, 0, 0),
    0x0e: QColor(0, 0, 0),
    0x37: QColor(0, 0, 0),
    0x01: QColor(0, 0, 0),
    0x0c: QColor(0, 0, 160),
    }

class Pattern:

    def __init__(self, path):
    
        d = open(path).read()
        start = struct.unpack("<h", d[:2])[0]
        data = d[start:]
        self.threads = data.split("\x80\x01")
        self.x, self.y = 0, 0
        
        self.colours = []
        colours = (start - 0x74)/8
        offset = 0x74
        for i in range(colours):
            self.colours.append(struct.unpack("<i", d[offset:offset+4])[0])
            offset += 4
    
    def show_coords(self, coords, pen, scene):
    
        first = True
        i = 0
        while i < len(coords):
            if coords[i:i+2] == "\x80\x02":
                i += 2
                self.x += struct.unpack("<b", coords[i])[0]
                self.y += struct.unpack("<b", coords[i+1])[0]
                i += 2
                x, y = self.x, self.y
                continue
            if coords[i:i+2] == "\x80\x10":
                break
            self.x += struct.unpack("<b", coords[i])[0]
            self.y += struct.unpack("<b", coords[i+1])[0]
            ellipse = scene.addEllipse(self.x, -self.y, 4, 4, QPen(QColor(200,200,200)))
            if not first:
                scene.addLine(x, -y, self.x, -self.y, pen)
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
    view.setScene(scene)
    view.show()
    
    p = Pattern(sys.argv[1])
    p.show(scene)
    sys.exit(app.exec_())
