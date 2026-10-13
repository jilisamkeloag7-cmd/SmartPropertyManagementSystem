
import urllib.request
from PySide6.QtGui import QPixmap, QPixmapCache


# Cache up to 50 MB of decoded images (default is 10 MB)
QPixmapCache.setCacheLimit(51200)


def load_pixmap(source: str) -> QPixmap:
    """
    Load a QPixmap from a local file path or an HTTP URL.
    Uses QPixmapCache so repeated loads are instant.
    """
    if not source:
        return QPixmap()

    cached = QPixmapCache.find(source)
    if cached is not None and not cached.isNull():
        return cached

    pix = QPixmap()

    if source.startswith("http"):
        try:
            with urllib.request.urlopen(source, timeout=5) as resp:
                data = resp.read()
            pix.loadFromData(data)
        except Exception as e:
            print(f"[image_cache] failed {source[:60]}: {e}")
    else:
        pix = QPixmap(source)

    if not pix.isNull():
        QPixmapCache.insert(source, pix)

    return pix
