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
from PyQt4.QtCore import QRect, QSize, Qt, SIGNAL
from PyQt4.QtGui import *

from jef2png import Convertor

class Canvas(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        self.convertor = None
        self.background = QBrush(Qt.white)
        self.picture = QPicture()
        self.scale = 1.0
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        #painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), self.background)
        painter.scale(self.scale, self.scale)
        painter.drawPicture(0, 0, self.picture)
        painter.end()
    
    def sizeHint(self):
    
        if self.convertor:
            return self.convertor.bounding_rect().size() * self.scale
        else:
            return QSize(0, 0)
    
    def setConvertor(self, convertor):
    
        self.convertor = convertor
        self.resize(convertor.bounding_rect().size())
        self.picture = QPicture()
        painter = QPainter()
        painter.begin(self.picture)
        convertor.show(painter)
        painter.end()
        self.update()
    
    def zoomIn(self):
    
        if self.scale >= 1:
            self.scale = min(self.scale + 1, 10)
        else:
            self.scale = min(self.scale + 0.1, 1)
        
        self.resize(self.sizeHint())
        self.update()
    
    def zoomOut(self):
    
        if self.scale > 1:
            self.scale = max(1, self.scale - 1)
        else:
            self.scale = max(0.1, self.scale - 0.1)
        
        self.resize(self.sizeHint())
        self.update()


class Viewer(QMainWindow):

    def __init__(self, parent = None):
    
        QMainWindow.__init__(self, parent)
        self.stitches_only = True
        self.path = ""
        
        self.canvas = Canvas()
        
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        openAction = self.fileMenu.addAction(self.tr("&Open"))
        openAction.setShortcut(QKeySequence.Open)
        self.connect(openAction, SIGNAL("triggered()"), self.openFileDialog)
        quitAction = self.fileMenu.addAction(self.tr("E&xit"))
        quitAction.setShortcut(self.tr("Ctrl+Q"))
        self.connect(quitAction, SIGNAL("triggered()"), self.close)
        
        self.viewMenu = self.menuBar().addMenu(self.tr("&View"))
        zoomInAction = self.fileMenu.addAction(self.tr("Zoom &In"))
        zoomInAction.setShortcut(QKeySequence.ZoomIn)
        self.connect(zoomInAction, SIGNAL("triggered()"), self.canvas.zoomIn)
        zoomOutAction = self.fileMenu.addAction(self.tr("Zoom &Out"))
        zoomOutAction.setShortcut(QKeySequence.ZoomOut)
        self.connect(zoomOutAction, SIGNAL("triggered()"), self.canvas.zoomOut)
        
        area = QScrollArea()
        area.setWidget(self.canvas)
        self.setCentralWidget(area)
        self.setWindowTitle(self.tr("Viewer for Janome Embroidery Files"))
    
    def openFile(self, path):
    
        self.canvas.setConvertor(Convertor(path, self.stitches_only))
    
    def openFileDialog(self):
    
        path = unicode(
            QFileDialog.getOpenFileName(
                self, self.tr("Open File"), os.path.split(self.path)[0],
                self.tr("Janome Embroidery Files (*.jef *.JEF)"))
            )
        
        if path:
            self.openFile(path)
            self.path = path


if __name__ == "__main__":

    app = QApplication(sys.argv)
    
    window = Viewer()
    
    if len(app.arguments()) > 1:
        window.openFile(app.arguments()[1])
    else:
        window.resize(QDesktopWidget().availableGeometry().size() * 0.5)
    window.show()
    sys.exit(app.exec_())
