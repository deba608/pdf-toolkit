"""Vector icon painter for PDF Toolkit.

Draws resolution-independent, crisp vector icons using QPainter and QPainterPath.
Zero external assets, 100% offline, crystal clear at any scale factor or DPI.
"""
from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QBrush, QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
)

from src.ui.theme import ACCENT, DANGER, TEXT, TEXT_FAINT, TEXT_MUTED


def _create_canvas(size: int = 24) -> tuple[QPixmap, QPainter]:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    return pixmap, painter


def get_icon(name: str, color: str = TEXT_MUTED, size: int = 20) -> QIcon:
    """Return a crisp QIcon for the given symbol name and color."""
    icon = QIcon()

    # Normal state
    pix_normal = _render_symbol(name, color, size)
    icon.addPixmap(pix_normal, QIcon.Normal, QIcon.Off)

    # Active / Selected state (accent or white)
    pix_active = _render_symbol(name, "#ffffff", size)
    icon.addPixmap(pix_active, QIcon.Active, QIcon.Off)
    icon.addPixmap(pix_active, QIcon.Selected, QIcon.Off)

    # Disabled state
    pix_disabled = _render_symbol(name, TEXT_FAINT, size)
    icon.addPixmap(pix_disabled, QIcon.Disabled, QIcon.Off)

    return icon


def get_pixmap(name: str, color: str = TEXT, size: int = 24) -> QPixmap:
    """Return a raw QPixmap for embedding in labels or paint events."""
    return _render_symbol(name, color, size)


def _render_symbol(name: str, color_hex: str, size: int = 24) -> QPixmap:
    pixmap, p = _create_canvas(size)
    c = QColor(color_hex)
    pen = QPen(c, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)

    # Unit coordinate system: 0.0 to 1.0 mapped to target size with padding
    s = float(size)
    pad = s * 0.12
    w = s - 2 * pad
    h = s - 2 * pad

    def u(x: float, y: float) -> QPointF:
        return QPointF(pad + x * w, pad + y * h)

    def ur(x: float, y: float, rw: float, rh: float) -> QRectF:
        return QRectF(pad + x * w, pad + y * h, rw * w, rh * h)

    name = name.lower().replace("-", "_").replace(" ", "_")

    if name in ("home", "library"):
        path = QPainterPath()
        path.moveTo(u(0.1, 0.45))
        path.lineTo(u(0.5, 0.1))
        path.lineTo(u(0.9, 0.45))
        path.lineTo(u(0.8, 0.45))
        path.lineTo(u(0.8, 0.9))
        path.lineTo(u(0.2, 0.9))
        path.lineTo(u(0.2, 0.45))
        path.closeSubpath()
        p.drawPath(path)
        # Door
        p.drawRect(ur(0.4, 0.55, 0.2, 0.35))

    elif name in ("merge", "combine"):
        # Two stacked cards merging
        p.drawRoundedRect(ur(0.1, 0.1, 0.55, 0.6), 2, 2)
        p.setBrush(QBrush(c))
        p.setPen(QPen(c, 1.4))
        p.drawRoundedRect(ur(0.35, 0.3, 0.55, 0.6), 2, 2)
        # Plus in the second card
        p.setPen(QPen(QColor("#0d1117"), 1.6, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(u(0.62, 0.48), u(0.62, 0.72))
        p.drawLine(u(0.50, 0.60), u(0.74, 0.60))

    elif name in ("split", "cut"):
        # Scissors
        p.drawEllipse(ur(0.1, 0.6, 0.28, 0.28))
        p.drawEllipse(ur(0.62, 0.6, 0.28, 0.28))
        p.drawLine(u(0.32, 0.65), u(0.75, 0.15))
        p.drawLine(u(0.68, 0.65), u(0.25, 0.15))

    elif name in ("rotate",):
        # Circular arrow
        rect = ur(0.15, 0.15, 0.7, 0.7)
        p.drawArc(rect, 45 * 16, 270 * 16)
        # Arrowhead
        arrow = QPainterPath()
        arrow.moveTo(u(0.75, 0.35))
        arrow.lineTo(u(0.88, 0.50))
        arrow.lineTo(u(0.62, 0.50))
        arrow.closeSubpath()
        p.setBrush(QBrush(c))
        p.drawPath(arrow)

    elif name in ("reorder", "sort"):
        # Up and Down arrows
        # Down arrow on left
        p.drawLine(u(0.3, 0.15), u(0.3, 0.85))
        p.drawLine(u(0.15, 0.70), u(0.3, 0.85))
        p.drawLine(u(0.45, 0.70), u(0.3, 0.85))
        # Up arrow on right
        p.drawLine(u(0.7, 0.85), u(0.7, 0.15))
        p.drawLine(u(0.55, 0.30), u(0.7, 0.15))
        p.drawLine(u(0.85, 0.30), u(0.7, 0.15))

    elif name in ("watermark", "stamp"):
        # Diagonal stamp frame
        p.drawRoundedRect(ur(0.15, 0.2, 0.7, 0.6), 3, 3)
        p.setPen(QPen(c, 1.4, Qt.DashLine))
        p.drawLine(u(0.25, 0.7), u(0.75, 0.3))

    elif name in ("compress", "optimize"):
        # Box with inward arrows
        p.drawRoundedRect(ur(0.15, 0.15, 0.7, 0.7), 3, 3)
        # Arrow pointing down into middle
        p.drawLine(u(0.5, 0.25), u(0.5, 0.65))
        p.drawLine(u(0.35, 0.50), u(0.5, 0.65))
        p.drawLine(u(0.65, 0.50), u(0.5, 0.65))
        # Base line
        p.drawLine(u(0.3, 0.75), u(0.7, 0.75))

    elif name in ("encrypt", "lock"):
        # Padlock
        p.drawRoundedRect(ur(0.2, 0.45, 0.6, 0.45), 3, 3)
        # Shackle
        shackle = QPainterPath()
        shackle.moveTo(u(0.32, 0.45))
        shackle.lineTo(u(0.32, 0.28))
        shackle.arcTo(ur(0.32, 0.12, 0.36, 0.32), 180, -180)
        shackle.lineTo(u(0.68, 0.45))
        p.drawPath(shackle)
        # Keyhole
        p.setBrush(QBrush(c))
        p.drawEllipse(ur(0.46, 0.60, 0.08, 0.08))

    elif name in ("decrypt", "unlock"):
        # Open padlock
        p.drawRoundedRect(ur(0.2, 0.45, 0.6, 0.45), 3, 3)
        shackle = QPainterPath()
        shackle.moveTo(u(0.32, 0.45))
        shackle.lineTo(u(0.32, 0.24))
        shackle.arcTo(ur(0.32, 0.08, 0.36, 0.32), 180, -180)
        shackle.lineTo(u(0.68, 0.30))
        p.drawPath(shackle)
        p.setBrush(QBrush(c))
        p.drawEllipse(ur(0.46, 0.60, 0.08, 0.08))

    elif name in ("to_images", "pdf_to_images", "export"):
        # Photo frame
        p.drawRoundedRect(ur(0.1, 0.15, 0.6, 0.65), 3, 3)
        p.drawEllipse(ur(0.22, 0.28, 0.12, 0.12))
        mountain = QPainterPath()
        mountain.moveTo(u(0.15, 0.70))
        mountain.lineTo(u(0.35, 0.45))
        mountain.lineTo(u(0.55, 0.70))
        p.drawPath(mountain)
        # Arrow pointing right
        p.drawLine(u(0.72, 0.5), u(0.92, 0.5))
        p.drawLine(u(0.84, 0.4), u(0.92, 0.5))
        p.drawLine(u(0.84, 0.6), u(0.92, 0.5))

    elif name in ("images_to_pdf", "import"):
        # Image frame on left, arrow pointing into document on right
        p.drawRoundedRect(ur(0.35, 0.15, 0.55, 0.7), 2, 2)
        # Plus
        p.drawLine(u(0.62, 0.38), u(0.62, 0.62))
        p.drawLine(u(0.50, 0.50), u(0.74, 0.50))
        # Arrow
        p.drawLine(u(0.08, 0.5), u(0.28, 0.5))
        p.drawLine(u(0.20, 0.4), u(0.28, 0.5))
        p.drawLine(u(0.20, 0.6), u(0.28, 0.5))

    elif name in ("batch", "automation", "lightning"):
        # Lightning bolt
        bolt = QPainterPath()
        bolt.moveTo(u(0.55, 0.08))
        bolt.lineTo(u(0.25, 0.55))
        bolt.lineTo(u(0.50, 0.55))
        bolt.lineTo(u(0.40, 0.92))
        bolt.lineTo(u(0.75, 0.42))
        bolt.lineTo(u(0.50, 0.42))
        bolt.closeSubpath()
        p.setBrush(QBrush(c))
        p.drawPath(bolt)

    elif name in ("pdf", "document", "file"):
        # Document with folded corner
        doc = QPainterPath()
        doc.moveTo(u(0.2, 0.1))
        doc.lineTo(u(0.6, 0.1))
        doc.lineTo(u(0.8, 0.3))
        doc.lineTo(u(0.8, 0.9))
        doc.lineTo(u(0.2, 0.9))
        doc.closeSubpath()
        p.drawPath(doc)
        # Fold
        p.drawLine(u(0.6, 0.1), u(0.6, 0.3))
        p.drawLine(u(0.6, 0.3), u(0.8, 0.3))

    elif name in ("add", "plus"):
        p.drawLine(u(0.5, 0.2), u(0.5, 0.8))
        p.drawLine(u(0.2, 0.5), u(0.8, 0.5))

    elif name in ("trash", "delete", "remove"):
        p.drawLine(u(0.2, 0.25), u(0.8, 0.25))
        p.drawRoundedRect(ur(0.28, 0.25, 0.44, 0.65), 2, 2)
        p.drawLine(u(0.4, 0.15), u(0.6, 0.15))
        p.drawLine(u(0.42, 0.38), u(0.42, 0.75))
        p.drawLine(u(0.58, 0.38), u(0.58, 0.75))

    elif name in ("search",):
        p.drawEllipse(ur(0.18, 0.18, 0.5, 0.5))
        p.drawLine(u(0.55, 0.55), u(0.82, 0.82))

    elif name in ("prev", "left"):
        p.drawLine(u(0.65, 0.25), u(0.35, 0.5))
        p.drawLine(u(0.35, 0.5), u(0.65, 0.75))

    elif name in ("next", "right"):
        p.drawLine(u(0.35, 0.25), u(0.65, 0.5))
        p.drawLine(u(0.65, 0.5), u(0.35, 0.75))

    elif name in ("zoom_in",):
        p.drawEllipse(ur(0.15, 0.15, 0.55, 0.55))
        p.drawLine(u(0.58, 0.58), u(0.85, 0.85))
        p.drawLine(u(0.42, 0.30), u(0.42, 0.54))
        p.drawLine(u(0.30, 0.42), u(0.54, 0.42))

    elif name in ("zoom_out",):
        p.drawEllipse(ur(0.15, 0.15, 0.55, 0.55))
        p.drawLine(u(0.58, 0.58), u(0.85, 0.85))
        p.drawLine(u(0.30, 0.42), u(0.54, 0.42))

    elif name in ("fit_width",):
        p.drawRoundedRect(ur(0.15, 0.25, 0.7, 0.5), 2, 2)
        p.drawLine(u(0.25, 0.5), u(0.75, 0.5))
        p.drawLine(u(0.35, 0.4), u(0.25, 0.5))
        p.drawLine(u(0.35, 0.6), u(0.25, 0.5))
        p.drawLine(u(0.65, 0.4), u(0.75, 0.5))
        p.drawLine(u(0.65, 0.6), u(0.75, 0.5))

    elif name in ("fit_page",):
        p.drawRoundedRect(ur(0.25, 0.15, 0.5, 0.7), 2, 2)
        p.drawLine(u(0.5, 0.25), u(0.5, 0.75))
        p.drawLine(u(0.4, 0.35), u(0.5, 0.25))
        p.drawLine(u(0.6, 0.35), u(0.5, 0.25))
        p.drawLine(u(0.4, 0.65), u(0.5, 0.75))
        p.drawLine(u(0.6, 0.65), u(0.5, 0.75))

    else:
        # Fallback circle dot
        p.setBrush(QBrush(c))
        p.drawEllipse(ur(0.35, 0.35, 0.3, 0.3))

    p.end()
    return pixmap
