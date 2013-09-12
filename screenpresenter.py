from math import sqrt
from random import randint, random

from PySide.QtCore import QEvent, QPointF
from PySide.QtGui import QBrush, QColor, QFont, QGraphicsScene, QKeyEvent, QPen, QPolygonF, QWidget

from grid import Grid
from griddetail import GridDetail
from hellogl import GLWidget

class ScreenPresenter(object):
    def __init__(self, view, uistack, widget):
        f = QFont('FreeMono')
        f.setWeight(QFont.Black)
        f.setPixelSize(16)

        grid = Grid()
        while grid.size < 3:
            subgrid = Grid(grid)
            subgrid.populate()
            grid = subgrid
        p = grid.faces.keys()[12]
        subgrid = Grid(grid)
        subgrid.populate(p)
        grid = subgrid
        while grid.size < 7:
            subgrid = Grid(grid)
            subgrid.populate(grid.faces.keys()[3])
            grid = subgrid

        self.grids = []
        prev = grid
        while prev is not None:
            self.grids.insert(0, prev)
            prev = prev.prev
        self.colors = [{}]
        for f in self.grids[0].faces:
            self.colors[-1][f] = tuple(3 * [0.5 * random() + 0.25])
        for g in self.grids[1:]:
            self.colors.append({})
            for f in g.faces:
                if f in g.prev.faces:
                    self.colors[-1][f] = self.colors[-2][f]
                else:
                    cs = [self.colors[-2][n][0] for n in g.prev.vertices[f] if n in self.colors[-2]]
                    self.colors[-1][f] = tuple(3 * [sum(cs)/len(cs) + 0.125 * random() - 0.0675])

        self._views = [GLWidget(self.grids[-1], self.colors, offset, view) for offset in (0, 180)]
        for v in self._views:
            view.angles.addWidget(v)

        self._detailview = view.detail
        self._detailview.scale(10, 10)

        view.layer.sliderMoved.connect(self.layer)
        view.detailLayer.sliderMoved.connect(self.detaillayer)

        self.detaillayer(-1)

        def detailevent(event):
            if (isinstance(event, QKeyEvent) and
                    event.text() == u'\t' and
                    event.type() == QEvent.ShortcutOverride):
                widget.keyPressEvent(QKeyEvent(
                    QEvent.KeyPress,
                    event.key(),
                    event.nativeModifiers(),
                    event.text(),
                    event.isAutoRepeat(),
                    event.count()))
                return True
            return QWidget.event(widget, event)

        widget.event = detailevent
        widget.keyPressEvent = self.key

        for l in view.layer, view.detailLayer:
            l.setMaximum(grid.size)
            l.setValue(grid.size)

        view.rotation.valueChanged.connect(self.rotate)

        view.layer.setValue(view.layer.maximum())

        self._uistack = uistack

    def key(self, event):
        facecount = len(self._detail.grid.faces)
        try:
            direction = {
                u"'": 'NW',
                u',': 'N',
                u'.': 'NE',
                u'a': 'SW',
                u'o': 'S',
                u'e': 'SE'}[event.text()]
        except KeyError:
            direction = None
        if direction is not None:
            detail = self._detail.move(direction)
        else:
            try:
                rotation = {
                    u'\t': 'CCW',
                    u'p': 'CW'}[event.text()]
            except KeyError:
                rotation = None
            if rotation is not None:
                detail = self._detail.rotate(rotation)
            else:
                detail = self._detail
        self._detail = detail
        self._detailview.setScene(self._detail.scene)
        if len(self._detail.grid.faces) != facecount:
            for v in self._views:
                v.update()
                v.redraw()

    def layer(self, depth):
        for v in self._views:
            v.layer(depth)

    def detaillayer(self, depth):
        self._detail = GridDetail(self.grids[depth], self.colors[depth], self.grids[depth].faces.keys()[0])
        self._detailview.setScene(self._detail.scene)

    def rotate(self, value):
        for v in self._views:
            v.rotate(value)
