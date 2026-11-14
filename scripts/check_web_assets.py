#!/usr/bin/env python3
"""Offline sanity check for Backscatter's two curated satellite web studies.

No NASA credentials or network requests needed. Run before publishing:
    python scripts/check_web_assets.py
"""
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
PUB=ROOT/"web"/"public"
EXPECTED={
    "kuttanad": {
        "base":PUB/"data", "dates":["2026-10-29","2026-11-10"],
        "layers":["oct29.png","nov10.png","change.png","hv_change.png","opera_oct29.png"],
        "expected_hv":True, "expected_crs":"EPSG:32643"
    },
    "assam": {
        "base":PUB/"data"/"assam", "dates":["2026-10-28","2026-11-09"],
        "layers":["before.png","after.png","change.png","opera.png"],
        "expected_hv":False,"expected_crs":"EPSG:32646"
    }
}

def png_size(p):
    header=p.read_bytes()[:24]
    if header[:8]!=b"\x89PNG\r\n\x1a\n":
        raise ValueError("Invalid PNG: "+str(p))
    return struct.unpack(">II",header[16:24])

def main():
    brand=PUB/"brand"/"backscatter-original.png"
    assert png_size(brand)==(1254,1254),"Original team logo missing or altered"
    assert png_size(PUB/"brand"/"favicon.png")== (180,180)
    for study,settings in EXPECTED.items():
        directory=settings["base"]
        metadata=json.loads((directory/"meta.json").read_text())
        h,w=metadata["rows"],metadata["cols"]
        if (directory/"pixels.bin").stat().st_size!=h*w*17:
            raise ValueError(study+": binary sample grid size mismatch")
        if metadata["crs"]!=settings["expected_crs"] or metadata["primary_dates"]!=settings["dates"]:
            raise ValueError(study+": incorrect georeferencing or observation dates")
        if len(metadata["image_coordinates_lonlat"])!=4:
            raise ValueError(study+": invalid overlay corners")
        for layer in settings["layers"]:
            if png_size(directory/layer)!=(w,h):
                raise ValueError(study+": overlay PNG dimensions mismatch: "+layer)
        if settings["expected_hv"]!=bool("hv_change.png" in settings["layers"]):
            raise ValueError(study+": unexpected polarization layer")
        print("OK",study,w,"x",h,"pixels",len(settings["layers"]),"raster layers",
              "shared area",metadata["statistics"]["radar_shared_valid_km2"],"km2")
    app=(ROOT/"web"/"src"/"main.jsx").read_text()
    if "maplibre-gl-worker.mjs?worker&url" not in app or "setWorkerUrl" not in app:
        raise ValueError("MapLibre v6 worker must be bundled explicitly")
    print("OK original logo, MapLibre worker, source-date labels and all image/binary grid dimensions")

if __name__=="__main__":
    main()
