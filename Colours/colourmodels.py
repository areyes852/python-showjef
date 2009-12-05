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
from PyQt4.QtCore import QAbstractTableModel, Qt, QVariant, \
                         SIGNAL, SLOT
from PyQt4.QtGui import *

import jef

class PatternColourItem(QStandardItem):

    def __init__(self, internal_colour):
    
        QStandardItem.__init__(self)
        
        self.internal_colour = internal_colour
        self.thread_offset = 0
        self.setColour(internal_colour)
    
    def colour(self):
    
        colours = jef.jef_colours.colour_mappings[self.internal_colour]
        
        # Use the value in the UserRole to determine which thread type to use.
        thread_type, code = colours[self.data(Qt.UserRole).toInt()[0]]
        name, colour = jef.jef_colours.known_colours[thread_type][code]
        return colour
    
    def internalColour(self):
    
        return self.internal_colour
    
    def threadOffset(self):
    
        return self.thread_offset
    
    def isChecked(self):
    
        return self.checkState() == Qt.Checked
    
    def setColour(self, internal_colour, thread_offset = 0):
    
        self.internal_colour = internal_colour
        self.thread_offset = thread_offset
        colours = jef.jef_colours.colour_mappings[internal_colour]
        thread_type, code = colours[thread_offset]
        name, colour = jef.jef_colours.known_colours[thread_type][code]
        
        self.setText(QApplication.translate("PatternColourItem", u"%1: %2 (%3)").arg(code).arg(name, thread_type))
        self.setData(QVariant(QColor(colour)), Qt.DecorationRole)
        self.setData(QVariant(Qt.Checked), Qt.CheckStateRole)
        self.setData(QVariant(thread_offset), Qt.UserRole)
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)


class PatternColourModel(QStandardItemModel):

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
        
            item = PatternColourItem(internal_colour)
            self.appendRow(item)


class ColourItem:

    """ColourItem
    
    Represents an internal Janome colour and its interpretations in different
    thread types.
    """
    
    def __init__(self, internal_colour):
    
        self.internal_colour = internal_colour
    
    def data(self, thread_type):
    
        colours = jef.jef_colours.colour_mappings[self.internal_colour]
        
        # Use the current column value to determine which thread type to use.
        thread_type, code = colours[thread_type]
        return thread_type, code
    
    def colour(self, thread_type = None):
    
        thread_type, code = self.data(thread_type)
        name, colour = jef.jef_colours.known_colours[thread_type][code]
        return colour
    
    def colourCount(self):
    
        return len(jef.jef_colours.colour_mappings[self.internal_colour])
    
    def name(self, thread_type = None):
    
        thread_type, code = self.data(thread_type)
        name, colour = jef.jef_colours.known_colours[thread_type][code]
        return name


class ColourModel(QAbstractTableModel):

    def __init__(self):
    
        QAbstractTableModel.__init__(self)
        
        self.connect(self, SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                     self, SIGNAL("colourChanged()"))
        
        # Create a list of rows for the model, each containing the thread
        # colours which correspond to a given internal colour.
        self.colours = []
        self.columns = 0
        
        keys = jef.jef_colours.colour_mappings.keys()
        keys.sort()
        
        for internal_colour in keys:
        
            item = ColourItem(internal_colour)
            self.columns = max(self.columns, item.colourCount())
            self.colours.append(item)
    
    def rowCount(self, parent):
    
        if parent.isValid():
            return -1
        else:
            return len(self.colours)
    
    def columnCount(self, parent):
    
        if parent.isValid():
            return -1
        else:
            return self.columns
    
    def data(self, index, role):
    
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        if not 0 <= row < self.colours:
            return QVariant()
        
        item = self.colours[row]
        if not 0 <= index.column() < item.colourCount():
            return QVariant()
        
        if role == Qt.DisplayRole:
            return QVariant(item.name(index.column()))
        elif role == Qt.DecorationRole:
            return QVariant(QColor(item.colour(index.column())))
        else:
            return QVariant()
    
    def internalColour(self, index):
    
        """Returns the internal colour of the item with the given index."""
        
        item = self.colours[index.row()]
        return item.internal_colour
    
    def threadOffset(self, index):
    
        """Returns the thread offset of the colour represented by the given index."""
        return index.column()
    
    def getIndex(self, internal_colour, thread_offset):
    
        row = 0
        for item in self.colours:
        
            if item.internal_colour == internal_colour:
                if 0 <= thread_offset < item.colourCount():
                    return self.createIndex(row, thread_offset)
                else:
                    return QModelIndex()
            
            row += 1
        
        return QModelIndex()
