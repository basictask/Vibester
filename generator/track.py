import qrcode
from typing import Dict, Tuple
from xml.etree import ElementTree
from qrcode.image.svg import SvgPathImage


class Track:
    def __init__(self, track: Dict):
        self.title = track.get("title", "")
        self.artist = track.get("artist", "")
        self.genre = track.get("genre", "")
        self.hash = track.get("hash", "")

        if track.get("year", None):
            self.year = int(track.get("year"))

    def qr_svg(self) -> Tuple[str, int]:
        """
        Render a QR code for the URL as SVG path, return also the side length
        (in SVG units, which by convention we map to mm).

        A box size of 10 means that every "pixel" in the code is 1mm, but we
        don't know how many pixels wide and tall the code is, so return that
        too, the "pixel size". Note, it is independent of the specified box.
        size, we always have to divide by 10.
        """
        qr = qrcode.make(self.hash, image_factory=SvgPathImage, box_size=8)
        return ElementTree.tostring(qr.path).decode("ascii"), qr.pixel_size / 10
