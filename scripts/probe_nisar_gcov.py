#!/usr/bin/env python3
"""Research-only NISAR GCOV pixel extraction probe for Kuttanad.

No inundation classifier, flood claims, or NISAR change map.
Uses a NASA Earthdata bearer token entered at a hidden prompt. No secrets saved.
Requirements: Python 3.9+, numpy, rasterio (rasterio's GDAL >= 3.9).
"""
import getpass
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

BBOX = (76.42, 9.40, 76.49, 9.47)
CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
COLLECTION = "C2854338529-ASF"
DATES = ("2026-09-14", "2026-09-26")
PAIR = "_113_A_006_4005_DHDH_"
DATASET = "//science/LSAR/GCOV/grids/frequencyA/HHHH"
CDN_HOSTS = {"d1mv8zhcvry6x4.cloudfront.net"}
MAX_SIDE = 128
OUT_DIR = Path.home() / "Downloads" / "backscatter-nisar-probe"

def is_nasa(host):
    return bool(host and (host.endswith(".nasa.gov") or
                          host.endswith(".earthdatacloud.nasa.gov")))

class SecureRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, url):
        host = urlsplit(url).hostname
        if urlsplit(url).scheme != "https" or not (is_nasa(host) or host in CDN_HOSTS):
            raise ValueError("Unexpected redirect host: " + str(host))
        child = super().redirect_request(req, fp, code, msg, headers, url)
        if host in CDN_HOSTS:
            for key in ("Authorization", "Cookie", "Proxy-Authorization"):
                child.remove_header(key)
                for actual in list(child.unredirected_hdrs):
                    if actual.lower() == key.lower():
                        child.unredirected_hdrs.pop(actual)
        return child

def find_granule(opener, date):
    params = {"collection_concept_id": COLLECTION,
              "bounding_box": ",".join(map(str, BBOX)),
              "temporal": date+"T00:00:00Z,"+date+"T23:59:59Z",
              "page_size": 100}
    with opener.open(CMR+"?"+urlencode(params), timeout=30) as r:
        entries = json.load(r)["feed"]["entry"]
    for entry in entries:
        gid = entry.get("producer_granule_id", "")
        if PAIR not in gid:
            continue
        for link in entry.get("links", []):
            url = link.get("href", "")
            if url.startswith("https://") and url.endswith(".h5"):
                if not is_nasa(urlsplit(url).hostname):
                    raise RuntimeError("Untrusted CMR download host")
                return gid, url
    raise RuntimeError("No matching GCOV scene found for "+date)

def obtain_signed_url(opener, url, token):
    req = Request(url, headers={"Authorization": "Bearer "+token,
                                "Range": "bytes=0-4095",
                                "User-Agent": "Backscatter-GCOV-Research/0.1"})
    with opener.open(req, timeout=40) as r:
        final_url = r.url
        signature = r.read(8)
        code = r.status
    if code != 206 or signature != b"\x89HDF\r\n\x1a\n":
        raise RuntimeError("Source did not return a valid partial HDF5 header")
    # GDAL gets only the CDN's temporary signed URL, NOT the Earthdata token.
    host = urlsplit(final_url).hostname
    if host not in CDN_HOSTS:
        raise RuntimeError("No allowlisted signed CDN redirect (final host: "+str(host)+")")
    return final_url

def read_sample(signed_url, date, gid):
    import numpy as np
    import rasterio
    from rasterio.windows import Window, from_bounds
    from rasterio.warp import transform_bounds
    version = tuple(int(v) for v in rasterio.__gdal_version__.split(".")[:2])
    driver = "HDF5" if version >= (3, 13) else "NETCDF"
    subdataset = '{}:"/vsicurl/{}":{}'.format(driver, signed_url, DATASET)
    opts = dict(GDAL_DISABLE_READDIR_ON_OPEN="YES",
                GDAL_HTTP_MULTIPLEX="YES",
                GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
                CPL_VSIL_CURL_CHUNK_SIZE="262144",
                CPL_VSIL_CURL_CACHE_SIZE="67108864",
                GDAL_HTTP_TIMEOUT="30", CPL_CURL_VERBOSE="NO")
    # Errors from GDAL may include the signed URL: never print them verbatim.
    try:
        with rasterio.Env(**opts):
            with rasterio.open(subdataset) as ds:
                if ds.count < 1 or not ds.crs:
                    raise RuntimeError("Raster has no usable georeferencing")
                bounds = transform_bounds("EPSG:4326", ds.crs, *BBOX)
                wanted = from_bounds(*bounds, transform=ds.transform)
                wanted = wanted.round_offsets().round_lengths()
                window = wanted.intersection(Window(0, 0, ds.width, ds.height))
                width = min(MAX_SIDE, int(window.width))
                height = min(MAX_SIDE, int(window.height))
                if not width or not height:
                    raise RuntimeError("AOI does not intersect GCOV grid")
                sample = Window(int(window.col_off+(window.width-width)//2),
                                int(window.row_off+(window.height-height)//2),
                                width, height)
                data = ds.read(1, window=sample, masked=True)
                power = np.asarray(data.filled(np.nan), dtype=np.float64)
                good = power[np.isfinite(power) & (power > 0)]
                if not len(good):
                    raise RuntimeError("No valid positive radar-power values")
                db = 10*np.log10(good)
                return {"date": date, "granule_id": gid, "variable": DATASET,
                        "gdal_version": rasterio.__gdal_version__,
                        "crs": str(ds.crs), "sample_shape": [height, width],
                        "window": [int(sample.col_off), int(sample.row_off), width, height],
                        "valid_positive_pixels": int(len(good)),
                        "sample_median_db": round(float(np.median(db)), 4),
                        "sample_db_p10": round(float(np.percentile(db, 10)), 4),
                        "sample_db_p90": round(float(np.percentile(db, 90)), 4),
                        "note": "Small NISAR HHHH sample, NOT flood detection or a comparable change map"}
    except Exception as exc:
        raise RuntimeError("GDAL extraction failed ("+type(exc).__name__+
                           "). Check ASF GDAL guide; no sensitive URL printed.") from None

def main():
    opener = build_opener(SecureRedirect())
    if "--preflight" in sys.argv:
        for date in DATES:
            name, _ = find_granule(opener, date)
            print(date, name)
        print("Preflight succeeded: scenes found. No protected data accessed.")
        return
    print("Kuttanad research probe: two 128x128-or-smaller NISAR HHHH samples")
    token = getpass.getpass("Earthdata bearer token (hidden): ").strip()
    if token.count(".") != 2:
        raise SystemExit("Invalid-looking Earthdata token")
    records = []
    for date in DATES:
        try:
            gid, source = find_granule(opener, date)
            signed = obtain_signed_url(opener, source, token)
            print(date, "authenticated; reading small radar sample ...", flush=True)
            record = read_sample(signed, date, gid)
            records.append(record)
            print(date, record["valid_positive_pixels"], "valid pixels, median",
                  record["sample_median_db"], "dB")
        except Exception as exc:
            # Unknown transport errors might include signed URLs; report only type.
            print(date, "FAILED:", str(exc) if type(exc) is RuntimeError else type(exc).__name__)
            return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR/"nisar_extraction_probe.json"
    out.write_text(json.dumps({"aoi_bbox_wgs84": BBOX, "samples": records}, indent=2)+"\n")
    print("Saved research-only results:", out)
    print("Reminder: these unaligned sample statistics are NOT a flood-change measurement.")

if __name__ == "__main__":
    main()
