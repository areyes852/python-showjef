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
from PyQt4.QtCore import QLine, QRect, QSize, Qt, SIGNAL, SLOT
from PyQt4.QtGui import *

import jef

class Zone:

    def __init__(self, rect, colour):
    
        self.rect = rect
        self.colour = colour
        self.subzones = []
        self.lines = []
    
    def paint(self, painter):
    
        pen = QPen(self.colour)
        painter.setPen(pen)
        painter.drawLines(self.lines)
    
    def paintWithin(self, painter, rect):
    
        if self.rect.intersects(rect):
        
            self.paint(painter)
            for subzone in self.subzones:
                subzone.paintWithin(painter, rect)

class Renderer:

    def __init__(self, path, stitches_only = False):
    
        self.jef = jef.Pattern(path)
        self.stitches_only = stitches_only
        self.rect = QRect()
        self.zones = []
        self._arrange_data()
    
    def _arrange_data(self):
    
        self.rect = QRect()
        
        for i in range(len(self.jef.coordinates)):
        
            coordinates = self.jef.coordinates[i]
            colour = QColor(*self.jef.colour_for_thread(i))
            
            lines = []
            xb, yb = [], []
            mx, my = 0, 0
            
            for op, x, y in coordinates:
                xb.append(x)
                yb.append(y)
                if op == "move":
                    mx, my = x, y
                elif op == "stitch":
                    line = QLine(mx, -my, x, -y)
                    lines.append(line)
                    mx, my = x, y
            
            xb = [min(xb), max(xb)]
            yb = [min(yb), max(yb)]
            rect = QRect(min(xb), -max(yb), max(xb) - min(xb), max(yb) - min(yb))
            self.rect = self.rect.united(rect)
            
            zone = Zone(rect, colour)
            zone.lines = lines
            self._partition_data(zone)
            self.zones.append(zone)
    
    def _partition_data(self, zone):
    
        subzone_width = zone.rect.width()/2
        subzone_height = zone.rect.height()/2
        
        if subzone_width < 100 or subzone_height < 100 or len(zone.lines) <= 10:
            return
        
        subzones = [
            Zone(QRect(zone.rect.x(), zone.rect.y(), subzone_width, subzone_height), zone.colour),
            Zone(QRect(zone.rect.x() + subzone_width, zone.rect.y(), subzone_width, subzone_height), zone.colour),
            Zone(QRect(zone.rect.x(), zone.rect.y() + subzone_height, subzone_width, subzone_height), zone.colour),
            Zone(QRect(zone.rect.x() + subzone_width, zone.rect.y() + subzone_height, subzone_width, subzone_height), zone.colour)
            ]
        
        lines = []
        
        for line in zone.lines:
            for subzone in subzones:
                # If a line is completely within a subzone, add it to the
                # subzone and ignore all other subzones.
                if subzone.rect.contains(line.p1()) and subzone.rect.contains(line.p2()):
                    subzone.lines.append(line)
                    break
            else:
                # If a line is not completely within a zone, add it to the list
                # of lines to keep in the zone.
                lines.append(line)
        
        zone.lines = lines
        
        for subzone in subzones:
            if subzone.lines:
                zone.subzones.append(subzone)
                self._partition_data(subzone)
    
    def bounding_rect(self):
    
        return self.rect
        
    def paint(self, painter, rect):
    
        # Transform the rectangle from window to pattern coordinates.
        rect = rect.translated(self.rect.topLeft())
        
        painter.save()
        painter.translate(-self.bounding_rect().topLeft())
        for zone in self.zones:
            zone.paintWithin(painter, rect)
        painter.restore()


class Canvas(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        self.renderer = None
        self.background = QBrush(Qt.white)
        self.picture = QPicture()
        self.scale = 1.0
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        #painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), self.background)
        painter.scale(self.scale, self.scale)
        if self.renderer:
            rect = painter.transform().inverted()[0].mapRect(event.rect())
            self.renderer.paint(painter, rect)
        painter.end()
    
    def sizeHint(self):
    
        if self.renderer:
            return self.renderer.bounding_rect().size() * self.scale
        else:
            return QSize(0, 0)
    
    def setRenderer(self, renderer):
    
        self.renderer = renderer
        self.resize(renderer.bounding_rect().size())
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


class ColourDockWidget(QDockWidget):

    def __init__(self, parent = None):
    
        QDockWidget.__init__(self, qApp.translate("ColourDockWidget", "Colours"), parent)
        
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.colourList = QListWidget()
        self.setWidget(self.colourList)


class Viewer(QMainWindow):

    def __init__(self, parent = None):
    
        QMainWindow.__init__(self, parent)
        self.stitches_only = True
        self.path = ""
        
        self.canvas = Canvas()
        
        colourDockAction = self._create_colour_dock_widget()
        
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        openAction = self.fileMenu.addAction(self.tr("&Open"))
        openAction.setShortcut(QKeySequence.Open)
        self.connect(openAction, SIGNAL("triggered()"), self.openFileDialog)
        quitAction = self.fileMenu.addAction(self.tr("E&xit"))
        quitAction.setShortcut(self.tr("Ctrl+Q"))
        self.connect(quitAction, SIGNAL("triggered()"), self.close)
        
        self.viewMenu = self.menuBar().addMenu(self.tr("&View"))
        zoomInAction = self.viewMenu.addAction(self.tr("Zoom &In"))
        zoomInAction.setShortcut(QKeySequence.ZoomIn)
        self.connect(zoomInAction, SIGNAL("triggered()"), self.canvas.zoomIn)
        zoomOutAction = self.viewMenu.addAction(self.tr("Zoom &Out"))
        zoomOutAction.setShortcut(QKeySequence.ZoomOut)
        self.connect(zoomOutAction, SIGNAL("triggered()"), self.canvas.zoomOut)
        
        self.toolsMenu = self.menuBar().addMenu(self.tr("&Tools"))
        self.toolsMenu.addAction(colourDockAction)
        
        area = QScrollArea()
        area.setWidget(self.canvas)
        self.setCentralWidget(area)
        self.setWindowTitle(self.tr("Viewer for Janome Embroidery Files"))
    
    def _create_colour_dock_widget(self):
    
        colourDockWidget = ColourDockWidget(self)
        self.addDockWidget(Qt.RightDockWidgetArea, colourDockWidget)
        colourDockWidget.hide()
        return colourDockWidget.toggleViewAction()
    
    def openFile(self, path):
    
        self.canvas.setRenderer(Renderer(path, self.stitches_only))
        self.path = path
    
    def openFileDialog(self):
    
        path = unicode(
            QFileDialog.getOpenFileName(
                self, self.tr("Open File"), os.path.split(self.path)[0],
                self.tr("Janome Embroidery Files (*.jef *.JEF)"))
            )
        
        if path:
            self.openFile(path)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    
    window = Viewer()
    
    if len(app.arguments()) > 1:
        window.openFile(app.arguments()[1])
    else:
        window.resize(QDesktopWidget().availableGeometry().size() * 0.5)
    window.show()
    sys.exit(app.exec_())
