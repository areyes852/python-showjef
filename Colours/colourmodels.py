#!/usr/bin/env python

"""
jefviewer.py - Display the contents of JEF files.

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

import os, sys
from PyQt4.QtCore import QLine, QObject, QPoint, QRect, QSize, Qt, QVariant, \
                         SIGNAL, SLOT
from PyQt4.QtGui import *

import jef

class ColourItem(QStandardItem):

    def __init__(self, internal_colour):
    
        QStandardItem.__init__(self)
        
        self.internal_colour = internal_colour
        self.setColour(internal_colour)
    
    def colour(self):
    
        colours = jef.jef_colours.colour_mappings[self.internal_colour]
        
        # Use the value in the UserRole to determine which thread type to use.
        thread_type, code = colours[self.data(Qt.UserRole).toInt()[0]]
        name, colour = jef.jef_colours.known_colours[thread_type][code]
        return colour
    
    def isChecked(self):
    
        return self.checkState() == Qt.Checked
    
    def setColour(self, internal_colour):
    
        self.internal_colour = internal_colour
        colours = jef.jef_colours.colour_mappings[internal_colour]
        thread_type, code = colours[0]
        name, colour = jef.jef_colours.known_colours[thread_type][code]
        
        self.setText(QApplication.translate("ColourItem", u"%1: %2 (%3)").arg(code).arg(name, thread_type))
        self.setData(QVariant(QColor(colour)), Qt.DecorationRole)
        self.setData(QVariant(Qt.Checked), Qt.CheckStateRole)
        self.setData(QVariant(0), Qt.UserRole)
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)


class ColourModel(QStandardItemModel):

    def __init__(self, background):
    
        QStandardItemModel.__init__(self)
        
        self.background = background
        self.pattern = None
        
        self.connect(self, SIGNAL("itemChanged(QStandardItem *)"),
                     self, SIGNAL("colourChanged()"))
    
    def setBackground(self, colour):
    
        self.background = colour
        self.emit(SIGNAL("colourChanged()"))
    
    def setColour(self, index, colour):
    
        item = self.itemFromIndex(index)
        item.setColour(colour)
        self.itemChanged.emit(item)
    
    def setPattern(self, pattern):
    
        self.pattern = pattern
        
        # Update the colours in the list with those from the pattern.
        self.clear()
        
        for internal_colour in pattern.colours:
        
            item = ColourItem(internal_colour)
            self.appendRow(item)
