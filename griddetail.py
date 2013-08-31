from math import sqrt

from PySide.QtCore import QPointF, Qt
from PySide.QtGui import QColor, QGraphicsScene, QPen, QPolygonF

N, NW, SW, S, SE, NE = range(6)
dirs = ['N', 'NW', 'SW', 'S', 'SE', 'NE']
vs = [(-1, sqrt(3)), (1, sqrt(3)), (2, 0), (1, -sqrt(3)), (-1, -sqrt(3)), (-2, 0)]
offsets = [(0, 2*sqrt(3)), (-3, sqrt(3)), (-3, -sqrt(3)), (0, -2*sqrt(3)), (3, -sqrt(3)), (3, sqrt(3))]
hexproto = QPolygonF([QPointF(*cs) for cs in vs])
pentproto = QPolygonF([QPointF(*cs) for cs in [(0, sqrt(3))] + vs[2:]])

class GridDetail(QGraphicsScene):
    def __init__(self, grids, colors, face):
        QGraphicsScene.__init__(self)

        self.grids = grids
        self.colors = colors
        self.face = face
        self.layer(len(self.grids) - 1)

    def layer(self, i):
        grid = self.grids[i]
        colors = self.colors[i]
        face = self.face
        if face not in grid.faces:
            face = grid.faces.keys()[0]
        if len(grid.faces[face]) == 5:
            for f in grid.faces:
                if len(grid.faces[f]) == 6:
                    face = f
                    break

        for item in self.items():
            self.removeItem(item)

        # initialize queue with face and arbitrarily chosen local North edge:
        # queue items are (face, direction traversed from, edge crossed, offset) tuples
        q = [(face, S, sorted(grid.faces[face][0:2]), (0,0))]
        pents = []
        seen = set()
        while len(q) > 0:
            face, whence, edge, offset = q.pop()
            if face not in seen:
                seen.add(face)
                vertices = grid.faces[face]
                if len(vertices) == 5:
                    pents.append((face, offset))
                    continue
                color = QColor(*[s * 255 for s in colors[face]])
                self.addPolygon(hexproto.translated(*offset), QPen(Qt.transparent), color)
                edges = [sorted(vs) for vs in zip(vertices, vertices[1:] + vertices[0:1])]
                # edges are in CCW order: find edge of origin in list to orient
                source = edges.index(edge)
                count = 0
                for border in edges[source + 1:] + edges[:source]:
                    commonfaces = list((grid.vertices[border[0]] & grid.vertices[border[1]]) - { face })
                    # one common face (if it exists in the grid)
                    if len(commonfaces) > 0:
                        nextdir = (whence + 1 + count) % 6
                        nextoffset = tuple([offset[i] + offsets[nextdir][i] for i in range(2)])
                        q.insert(0, (commonfaces[0], (nextdir + 3) % 6, border, nextoffset))
                    count += 1
        for face, offset in pents:
            populated = []
            for ni in range(len(offsets)):
                if self.itemAt(*[offset[i] + offsets[ni][i] for i in range(2)]) is not None:
                    if len(populated) > 0 and populated[-1] + 1 != ni:
                        ni -= 6
                    populated.append(ni)
            base = sorted(populated)[len(populated)/2] if len(populated) > 0 else 0

            color = QColor(*[s * 255 for s in colors[face]])
            polygon = self.addPolygon(pentproto.translated(*offset), QPen(Qt.transparent), color)
            polygon.setTransformOriginPoint(*offset)
            polygon.setRotation(60 * (base + 3))
        self.update()
