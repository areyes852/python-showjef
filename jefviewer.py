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
from Colours import colourmodels, colourpalette

class Zone:

    def __init__(self, rect, colour_item):
    
        self.rect = rect
        self.colour_item = colour_item
        self.subzones = []
        self.lines = []
    
    def paint(self, painter):
    
        if self.colour_item.isChecked():
            pen = QPen(QColor(self.colour_item.colour()))
            painter.setPen(pen)
            painter.drawLines(self.lines)
    
    def paintWithin(self, painter, rect):
    
        if self.rect.intersects(rect):
        
            self.paint(painter)
            for subzone in self.subzones:
                subzone.paintWithin(painter, rect)

class Renderer:

    def __init__(self, pattern, colourModel, stitches_only = False):
    
        self.pattern = pattern
        self.colourModel = colourModel
        self.stitches_only = stitches_only
        self.rect = QRect()
        self.zones = []
        self._arrange_data()
    
    def _arrange_data(self):
    
        self.rect = QRect()
        
        for i in range(len(self.pattern.coordinates)):
        
            coordinates = self.pattern.coordinates[i]
            colour_item = self.colourModel.item(i)
            
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
            
            zone = Zone(rect, colour_item)
            zone.lines = lines
            self._partition_data(zone)
            self.zones.append(zone)
    
    def _partition_data(self, zone):
    
        subzone_width = zone.rect.width()/2
        subzone_height = zone.rect.height()/2
        
        if subzone_width < 100 or subzone_height < 100 or len(zone.lines) <= 10:
            return
        
        subzones = [
            Zone(QRect(zone.rect.x(), zone.rect.y(), subzone_width, subzone_height), zone.colour_item),
            Zone(QRect(zone.rect.x() + subzone_width, zone.rect.y(), subzone_width, subzone_height), zone.colour_item),
            Zone(QRect(zone.rect.x(), zone.rect.y() + subzone_height, subzone_width, subzone_height), zone.colour_item),
            Zone(QRect(zone.rect.x() + subzone_width, zone.rect.y() + subzone_height, subzone_width, subzone_height), zone.colour_item)
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

    def __init__(self, colourModel, parent = None):
    
        QWidget.__init__(self, parent)
        
        self.colourModel = colourModel
        self.connect(colourModel, SIGNAL("colourChanged()"), self.update)
        self.connect(colourModel, SIGNAL("backgroundChanged()"), self.update)
        
        self.renderer = None
        self.scale = 1.0
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        #painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), self.colourModel.background)
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
        self.resize(self.sizeHint())
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


class CanvasView(QScrollArea):

    def __init__(self, canvas, parent = None):
    
        QScrollArea.__init__(self, parent)
        self.canvas = canvas
        self.setWidget(canvas)
        self.dragging = False
        self.dragStartPos = QPoint()
        canvas.setCursor(Qt.OpenHandCursor)
    
    def mousePressEvent(self, event):
    
        if event.button() == Qt.LeftButton:
            self.canvas.dragging = True
            self.canvas.setCursor(Qt.ClosedHandCursor)
            self.dragStartPos = QPoint(event.pos())
    
    def mouseMoveEvent(self, event):
    
        if self.canvas.dragging:
            change = event.pos() - self.dragStartPos
            self.dragStartPos = QPoint(event.pos())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - change.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - change.y())
    
    def mouseReleaseEvent(self, event):
    
        if event.button() == Qt.LeftButton:
            self.canvas.dragging = False
            self.canvas.setCursor(Qt.OpenHandCursor)


class ColourDockWidget(QDockWidget):

    def __init__(self, colourModel, parent = None):
    
        QDockWidget.__init__(self, qApp.translate("ColourDockWidget", "&Colours"), parent)
        
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.colourModel = colourModel
        self.colourPalette = colourpalette.ColourPalette(self)
        
        colourList = QTreeView()
        colourList.header().hide()
        colourList.setRootIsDecorated(False)
        colourList.setModel(self.colourModel)
        
        colourList.activated.connect(self.editColour)
        
        self.backgroundButton = QPushButton(self.tr("&Background Colour"))
        self.connect(self.backgroundButton, SIGNAL("clicked()"), self.selectBackground)
        self._set_background_button_colour(colourModel.background)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(colourList)
        layout.addWidget(self.backgroundButton)
        
        self.setWidget(widget)
    
    def editColour(self, index):
    
        item = self.colourModel.itemFromIndex(index)
        
        if self.colourPalette.exec_(item) == QDialog.Accepted:
        
            colour = self.colourPalette.selectedInternalColour()
            thread_type = self.colourPalette.selectedThreadType()
            if colour and thread_type:
                item.setColour(colour, thread_type)
    
    def selectBackground(self):
    
        colour = QColorDialog.getColor(self.colourModel.background, self)
        if colour.isValid():
            self.setBackground(colour)
    
    def setBackground(self, colour):
    
        self._set_background_button_colour(colour)
        self.colourModel.setBackground(colour)
    
    def _set_background_button_colour(self, colour):
    
        icon_size = QApplication.style().pixelMetric(QStyle.PM_ButtonIconSize)
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(colour)
        self.backgroundButton.setIcon(QIcon(pixmap))
    
    def setPattern(self, pattern):
    
        self.colourModel.setPattern(pattern)


class Viewer(QMainWindow):

    def __init__(self, parent = None):
    
        QMainWindow.__init__(self, parent)
        
        # Pattern-related attributes
        self.stitches_only = True
        self.path = ""
        self.pattern = None
        self.colourModel = colourmodels.PatternColourModel(QColor(Qt.white))
        self.connect(self.colourModel, SIGNAL("colourChanged()"), self.setModified)
        
        self.canvas = Canvas(self.colourModel)
        
        colourDockAction = self._create_colour_dock_widget()
        
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        
        openAction = self.fileMenu.addAction(self.tr("&Open"))
        openAction.setShortcut(QKeySequence.Open)
        self.connect(openAction, SIGNAL("triggered()"), self.openFileDialog)
        
        saveAsAction = self.fileMenu.addAction(self.tr("Save &As..."))
        self.connect(saveAsAction, SIGNAL("triggered()"), self.saveFileDialog)
        
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
        
        area = CanvasView(self.canvas)
        area.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(area)
        self.setWindowTitle(self.tr("Viewer for Janome Embroidery Files [*]"))
    
    def _create_colour_dock_widget(self):
    
        self.colourDockWidget = ColourDockWidget(self.colourModel, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colourDockWidget)
        self.colourDockWidget.hide()
        return self.colourDockWidget.toggleViewAction()
    
    def openFile(self, path):
    
        path = unicode(path)
        self.pattern = jef.Pattern(path)
        
        qApp.setOverrideCursor(Qt.WaitCursor)
        self.path = path
        self.colourDockWidget.setPattern(self.pattern)
        self.canvas.setRenderer(Renderer(self.pattern, self.colourModel, self.stitches_only))
        self.setWindowTitle(self.tr("%1 - Viewer for Janome Embroidery Files [*]").arg(path))
        qApp.restoreOverrideCursor()
    
    def openFileDialog(self):
    
        path = unicode(
            QFileDialog.getOpenFileName(
                self, self.tr("Open File"), os.path.split(self.path)[0],
                self.tr("Janome Embroidery Files (*.jef *.JEF)"))
            )
        
        if path:
            self.openFile(path)
    
    def saveFile(self, path):
    
        path = unicode(path)
        
        qApp.setOverrideCursor(Qt.WaitCursor)
        saved = self.pattern.save(path)
        qApp.restoreOverrideCursor()
        
        if saved:
            self.setWindowModified(False)
            self.path = path
        else:
            QMessageBox.warning(self, self.tr("Failed to save file."))
    
    def saveFileDialog(self):
    
        path = unicode(
            QFileDialog.getSaveFileName(
                self, self.tr("Save File"), os.path.split(self.path)[0],
                self.tr("Janome Embroidery Files (*.jef *.JEF)"))
            )
        
        if path:
            self.saveFile(path)
    
    def setModified(self):
    
        self.setWindowModified(True)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    
    window = Viewer()
    
    if len(app.arguments()) > 1:
        window.openFile(app.arguments()[1])
    else:
        window.resize(QDesktopWidget().availableGeometry().size() * 0.75)
    window.show()
    sys.exit(app.exec_())
