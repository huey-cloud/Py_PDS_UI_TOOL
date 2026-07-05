"""개략화된 한국 지도 위에 공장(사이트) 마커를 표시하고 클릭 이벤트를 전달하는 위젯."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
)

from src.data.sites import COMPANY_COLOR, SITES, Site

_ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets"
_MARKER_RADIUS = 9.0


class _MarkerItem(QGraphicsEllipseItem):
    """클릭 가능한 사이트 마커. 부모 뷰가 넘겨준 콜백을 눌렀을 때 호출한다."""

    def __init__(self, site: Site, color: str, on_click):
        r = _MARKER_RADIUS
        super().__init__(-r, -r, r * 2, r * 2)
        x, y = site.map_xy()
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(color)))
        self.setPen(QPen(QColor("#ffffff"), 2))
        self.setZValue(10)
        self.setToolTip(f"{site.name}\n(클릭해서 상세 보기)")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAcceptHoverEvents(True)
        self._site = site
        self._on_click = on_click

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 1.5)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        self._on_click(self._site)
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        r = _MARKER_RADIUS * 1.25
        self.setRect(-r, -r, r * 2, r * 2)
        self.setPen(QPen(QColor("#333333"), 2.5))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        r = _MARKER_RADIUS
        self.setRect(-r, -r, r * 2, r * 2)
        self.setPen(QPen(QColor("#ffffff"), 2))
        super().hoverLeaveEvent(event)


class _LabelItem(QGraphicsPathItem):
    """흰색 외곽선(halo)이 있는 텍스트 라벨. 옅은 색 지도 위에서도 잘 읽힌다."""

    def __init__(self, text: str, x: float, y: float):
        font = QFont("Malgun Gothic", 9)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        path = QPainterPath()
        path.addText(0, 0, font, text)
        super().__init__(path)
        self.setPos(x, y)
        self.setPen(QPen(QColor("#ffffff"), 3))
        self.setBrush(QBrush(QColor("#2b2b2b")))
        self.setZValue(11)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, False)


class MapView(QGraphicsView):
    """사이트 마커를 클릭하면 site_selected 시그널을 발생시키는 지도 뷰."""

    site_selected = Signal(object)  # Site 전달

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._load_map_background()
        self._add_markers()

    def _load_map_background(self) -> None:
        svg_path = _ASSETS_DIR / "korea_map.svg"
        svg_item = QGraphicsSvgItem(str(svg_path))
        svg_item.setZValue(0)
        self._scene.addItem(svg_item)
        self._scene.setSceneRect(svg_item.boundingRect())

    def _add_markers(self) -> None:
        for site in SITES:
            color = COMPANY_COLOR.get(site.company, "#666666")
            marker = _MarkerItem(site, color, self._on_marker_clicked)
            self._scene.addItem(marker)

            x, y = site.map_xy()
            short_label = site.name.split(" ", 1)[-1]  # "평택캠퍼스" 등만 표시
            label = _LabelItem(short_label, x + _MARKER_RADIUS + 4, y + 4)
            self._scene.addItem(label)

    def _on_marker_clicked(self, site: Site) -> None:
        self.site_selected.emit(site)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
