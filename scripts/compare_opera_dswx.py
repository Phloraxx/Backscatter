#!/usr/bin/env python3
"""Backscatter data feasibility: compare two real OPERA DSWx-S1 water rasters.

Requirements: python3 -m pip install numpy rasterio matplotlib
This is a scientific *data check*, not a NISAR flood classifier.
The Earthdata bearer token is read with getpass; never saved to disk.
"""
from __future__ import annotations

import getpass
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
DSWX_COLLECTION = "C2949811996-POCLOUD"
AOI = (76.42, 9.40, 76.49, 9.47)  # lon_min, lat_min, lon_max, lat_max
TILE = "T43PFL"  # same OPERA/MGRS tile on both dates
DATES = ("2026-09-15", "2026-09-27")
OUT = Path.home() / "Downloads" / "backscatter-opera-check"
MAX_TIFF_BYTES = 25 * 1024 * 1024

# Only exact previously observed NASA CDN endpoints are allowed. The token
# is stripped whenever the request is redirected to an object-store CDN.
CDNS = {
    "deotb6e7tfubr.cloudfront.net",
    "d1mv8zhcvry6x4.cloudfront.net",
    "podaac-ops-cumulus-protected.s3.us-west-2.amazonaws.com",
}


def allowed_host(host: str | None) -> bool:
    return bool(host and (host.endswith(".nasa.gov") or host in CDNS))


class RestrictedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != "https" or not allowed_host(parsed.hostname):
            raise ValueError("Blocked untrusted redirect host: " + str(parsed.hostname))
        child = super().redirect_request(req, fp, code, msg, headers, newurl)
        # A signed CloudFront URL does not need the NASA user token.
        if parsed.hostname in CDNS:
            for name in ("Authorization", "Cookie", "Proxy-Authorization"):
                child.remove_header(name)
                for stored_key in list(child.unredirected_hdrs):
                    if stored_key.lower() == name.lower():
                        child.unredirected_hdrs.pop(stored_key, None)
        return child


opener = build_opener(RestrictedRedirect())


def find_wtr(date):
    q = {
        "collection_concept_id": DSWX_COLLECTION,
        "bounding_box": ",".join(map(str, AOI)),
        "temporal": f"{date}T00:00:00Z,{date}T23:59:59Z",
        "page_size": 100,
    }
    with opener.open(CMR + "?" + urlencode(q), timeout=25) as r:
        entries = json.load(r)["feed"]["entry"]
    for x in entries:
        name = x.get("producer_granule_id", "")
        if TILE not in name:
            continue
        for link in x.get("links", []):
            url = link.get("href", "")
            if url.startswith("https://") and url.endswith("_B01_WTR.tif"):
                if not allowed_host(urlsplit(url).hostname):
                    raise ValueError("Unexpected WTR download host")
                return name, url
    raise RuntimeError(f"No WTR product found on {date} for tile {TILE}")


def get_tiff(token, date):
    name, url = find_wtr(date)
    path = OUT / f"OPERA_{TILE}_{date}_WTR.tif"
    print(f"{date}: {name}")
    if not path.exists():
        req = Request(url, headers={
            "Authorization": "Bearer " + token,
            "User-Agent": "Backscatter-Research-ReadOnly/1.0",
        })
        with opener.open(req, timeout=45) as r:
            data = r.read(MAX_TIFF_BYTES + 1)
        if len(data) > MAX_TIFF_BYTES:
            raise RuntimeError("The WTR TIFF exceeds the 25 MB safety limit")
        if data[:4] not in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
            raise RuntimeError("Downloaded file is not a TIFF")
        path.write_bytes(data)
        print(f"  Downloaded {len(data):,} bytes to {path.name}")
    return path


def analyze(files):
    import numpy as np
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.warp import transform_bounds

    arrays = []
    windows_meta = []
    for path in files:
        with rasterio.open(path) as ds:
            if not ds.crs or not ds.crs.is_projected or ds.crs.linear_units not in ('metre', 'meter', 'metres', 'meters'):
                raise RuntimeError('Expected a projected, metre-based raster for area estimates')
            bbox = transform_bounds("EPSG:4326", ds.crs, *AOI, densify_pts=21)
            window = from_bounds(*bbox, transform=ds.transform)
            window = window.round_offsets().round_lengths()
            data = ds.read(1, window=window, boundless=True, fill_value=255)
            wt = ds.window_transform(window)
            arrays.append(data)
            windows_meta.append((str(ds.crs), tuple(wt), data.shape))
            print(f"  {path.name}: CRS={ds.crs}, window={data.shape}, unique_classes="
                  f"{dict(zip(*np.unique(data, return_counts=True)))}")

    if windows_meta[0] != windows_meta[1]:
        raise RuntimeError("The two rasters do not align exactly; reproject before comparison")
    before, after = arrays
    # OPERA DSWx-S1 V1: 0=not water, 1=open water, 3=inundated vegetation;
    # 250/251/255 are masked/invalid for the simple binary comparison.
    valid = np.isin(before, (0, 1, 3)) & np.isin(after, (0, 1, 3))
    water0 = np.isin(before, (1, 3))
    water1 = np.isin(after, (1, 3))
    new = valid & ~water0 & water1
    lost = valid & water0 & ~water1
    unchanged_water = valid & water0 & water1
    unchanged_land = valid & ~water0 & ~water1
    # OPERA DSWx-S1 is stored in a projected 30-m MGRS grid.
    crs, transform, shape = windows_meta[0]
    import affine
    aff = affine.Affine(*transform[:6])
    pixel_m2 = abs(aff.a * aff.e - aff.b * aff.d)
    counts = {
        "valid_both": int(valid.sum()),
        "new_water": int(new.sum()),
        "lost_water": int(lost.sum()),
        "water_both": int(unchanged_water.sum()),
        "land_both": int(unchanged_land.sum()),
    }
    areas = {key + "_km2": round(v * pixel_m2 / 1_000_000, 5) for key, v in counts.items()}
    result = {"area_bbox_wgs84": AOI, "tile": TILE, "dates": DATES,
              "grid_crs": crs, "pixel_area_m2": pixel_m2,
              "counts": counts, "areas": areas,
              "note": "OPERA observational comparison only. Not ground truth or NISAR classification."}
    (OUT / "opera_comparison.json").write_text(json.dumps(result, indent=2))
    print("\nRESULT (valid pixels shared across both dates only):")
    print(json.dumps(areas, indent=2))
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        # Map classes by index: 0=nonwater, 1=water, 2=masked.
        pre = np.where(np.isin(before, (1, 3)), 1, np.where(before == 0, 0, 2))
        post = np.where(np.isin(after, (1, 3)), 1, np.where(after == 0, 0, 2))
        change = np.where(~valid, 0, np.where(new, 2, np.where(lost, 3, 1)))
        fig, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
        for ax, arr, title in zip(axes, [pre, post, change],
                                  ["OPERA Sept 15", "OPERA Sept 27", "Observed change"]):
            ax.imshow(arr, interpolation='nearest', cmap='viridis', vmin=0, vmax=3)
            ax.set_title(title)
            ax.axis('off')
        fig.suptitle('Kuttanad candidate water changes — OPERA DSWx-S1 (not NISAR)')
        fig.savefig(OUT / 'opera_comparison.png', dpi=150)
        plt.close(fig)
        print("Map preview: ", OUT / 'opera_comparison.png')
    except ImportError:
        print('Plot skipped: optional matplotlib package not installed.')
    print('Summary:', OUT / 'opera_comparison.json')
    if counts['valid_both'] == 0:
        print('WARNING: No shared valid pixels in AOI. Choose another tile/date/region.')


def main():
    token = getpass.getpass('Earthdata bearer token (hidden): ').strip()
    if token.count('.') != 2:
        raise SystemExit('Invalid-looking token')
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        paths = [get_tiff(token, date) for date in DATES]
        del token
        analyze(paths)
    except (HTTPError, URLError) as e:
        print('Download error:', getattr(e, 'code', type(e).__name__))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
