#!/usr/bin/env python

"""
jbf2png.py - Converts the contents of JBF thumbnail files to PNG images.

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

import sets, struct, sys
from PyQt4.QtGui import *

if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s <JBF file> <PNG file>\n" % sys.argv[0])
        sys.exit(1)
    
    jbf_file = sys.argv[1]
    png_file = sys.argv[2]
    
    data = open(jbf_file, "rb").read()
    x_offset = struct.unpack(">H", data[8:10])[0]
    length = struct.unpack(">I", data[20:24])[0]
    width, height = struct.unpack("<II", data[24 + length + 4:24 + length + 12])
    
    padding = (4 - (width % 4)) % 4
    
    i = 24 + x_offset
    thumbnail_data = ""
    entries = sets.Set()
    for j in range(height):
    
        row = data[i:i+width]+(padding*"\x00")
        for k in row:
            entries.add(ord(k))
        thumbnail_data += row
        i += width
    
    image = QImage(thumbnail_data, width, height, QImage.Format_Indexed8)
    image.setColorTable(range(max(entries)+1))
    for entry in entries:
        image.setColor(entry, qRgb(0, 0, 0))
    image.setColor(0, qRgb(255, 255, 255))
    
    image.save(png_file)
    sys.exit()
