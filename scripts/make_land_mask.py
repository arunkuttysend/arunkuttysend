#!/usr/bin/env python3
"""One-off: rasterise Natural Earth 1:110m land polygons into a dot mask.

    python3 scripts/make_land_mask.py ne_110m_land.geojson > scripts/data/land-mask.txt

Natural Earth is public domain (https://www.naturalearthdata.com). Only the
derived mask is committed; the build never needs network access.
"""
from __future__ import annotations

import json
import sys

STEP = 2.25           # degrees between dots
LAT_MAX, LAT_MIN = 76.0, -56.0


def _inside(lon: float, lat: float, ring: list[list[float]]) -> bool:
    """Even-odd ray casting; fine for 1:110m rings (no antimeridian-crossers that matter)."""
    hit = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][:2]
        xj, yj = ring[j][:2]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def main(path: str) -> None:
    feats = json.load(open(path, encoding="utf-8"))["features"]
    polys: list[list[list[list[float]]]] = []
    for f in feats:
        g = f["geometry"]
        polys.extend([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"])
    boxes = [(min(p[0] for p in poly[0]), max(p[0] for p in poly[0]),
              min(p[1] for p in poly[0]), max(p[1] for p in poly[0])) for poly in polys]
    print(f"# step={STEP} lat={LAT_MAX}..{LAT_MIN} lon=-180..180 source=NaturalEarth ne_110m_land (public domain)")
    lat = LAT_MAX
    while lat >= LAT_MIN - 1e-9:
        row = []
        lon = -180.0 + STEP / 2
        while lon < 180.0:
            land = False
            for poly, (x0, x1, y0, y1) in zip(polys, boxes):
                if x0 <= lon <= x1 and y0 <= lat <= y1 and _inside(lon, lat, poly[0]) \
                        and not any(_inside(lon, lat, hole) for hole in poly[1:]):
                    land = True
                    break
            row.append("1" if land else "0")
            lon += STEP
        print("".join(row))
        lat -= STEP


if __name__ == "__main__":
    main(sys.argv[1])
