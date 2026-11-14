#!/usr/bin/env python3
"""Extract a small, aligned pair of validated NISAR GCOV backscatter rasters.

NASA Space Apps 2026 / Backscatter, Team Afterimage.
Inputs: NISAR_L2_GCOV_V1 (2026-10-29 and 2026-11-10), Kuttanad, Kerala.
Read-only source access: CMR + authenticated HTTP Range -> short-lived signed CDN URL
-> GDAL /vsicurl, with only a small AOI read into memory.
Outputs are independent radar measurements, NOT an inundation/flood classification.

Run --preflight to verify both scenes without credentials, --self-test for local math.
Run without flags to getpass() the Earthdata token; never passed via CLI or saved.
Requires Python >=3.9, rasterio (GDAL >=3.9), numpy and optionally matplotlib.
"""
import getpass
import json
import math
import sys
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

COLLECTION = "C3622241360-ASF"
CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
AOI = (76.42, 9.40, 76.49, 9.47)  # lon_min, lat_min, lon_max, lat_max
DATES = ("2026-10-29", "2026-11-10")
PAIR_ID = "_077_D_084_4005_DHDH_"
PROCESSOR = "_P05036_"
VAR = "//science/LSAR/GCOV/grids/frequencyA/HHHH"
CRS = "EPSG:32643"  # UTM zone 43 North, metres
RESOLUTION_M = 30
OUT = Path.home() / "Downloads" / "backscatter-validated-kuttanad"
CDN_HOSTS = {
    "d1mv8zhcvry6x4.cloudfront.net",  # previously observed ASF protected-data CDN
}
MAX_SRC_SIDE = 1500

def is_nasa_host(host):
    return bool(host and (host.endswith(".nasa.gov") or
                          host.endswith(".earthdatacloud.nasa.gov")))

class ProtectedRedirect(HTTPRedirectHandler):
    """Refuse unknown redirects and prevent bearer-token leakage to CDNs."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = urlsplit(newurl).hostname
        if urlsplit(newurl).scheme != "https" or not (
            is_nasa_host(host) or host in CDN_HOSTS
        ):
            raise ValueError("Unexpected HTTPS redirect hostname: " + str(host))
        child = super().redirect_request(req, fp, code, msg, headers, newurl)
        if host in CDN_HOSTS:
            for key in ("Authorization", "Cookie", "Proxy-Authorization"):
                child.remove_header(key)
                for saved in list(child.unredirected_hdrs):
                    if saved.lower() == key.lower():
                        child.unredirected_hdrs.pop(saved, None)
        return child

def discover(date):
    params = {"collection_concept_id": COLLECTION,
              "bounding_box": ",".join(map(str, AOI)),
              "temporal": date+"T00:00:00Z,"+date+"T23:59:59Z",
              "page_size": 100}
    url = CMR+"?"+urlencode(params)
    with build_opener(ProtectedRedirect()).open(url, timeout=25) as res:
        records = json.load(res)["feed"]["entry"]
    for record in records:
        name = record.get("producer_granule_id", "")
        if PAIR_ID not in name or PROCESSOR not in name:
            continue
        for link in record.get("links", []):
            href = link.get("href", "")
            if (href.startswith("https://") and href.endswith(".h5") and
                    is_nasa_host(urlsplit(href).hostname)):
                return name, href
    raise RuntimeError("No matching validated GCOV observation for "+date)

def signed_url(source, token):
    req = Request(source, headers={"Authorization": "Bearer "+token,
                                  "Range": "bytes=0-4095",
                                  "User-Agent": "Backscatter/Validated-GCOV-1.0"})
    with build_opener(ProtectedRedirect()).open(req, timeout=40) as res:
        status, first8, url = res.status, res.read(8), res.url
    if status != 206 or first8 != b"\x89HDF\r\n\x1a\n":
        raise RuntimeError("Invalid authenticated HDF5 range response")
    if urlsplit(url).hostname not in CDN_HOSTS:
        raise RuntimeError("No recognized signed CDN target; update vetted host allowlist")
    return url

def make_grid():
    from rasterio.warp import transform_bounds
    from rasterio.transform import from_origin
    left, bottom, right, top = transform_bounds("EPSG:4326", CRS, *AOI)
    width = math.ceil((right-left)/RESOLUTION_M)
    height = math.ceil((top-bottom)/RESOLUTION_M)
    return from_origin(left, top, RESOLUTION_M, RESOLUTION_M), width, height

def extract_one(date, gid, url, target):
    import numpy as np
    import rasterio
    from rasterio.windows import Window, from_bounds
    from rasterio.warp import reproject, Resampling, transform_bounds

    version = tuple(int(x) for x in rasterio.__gdal_version__.split(".")[:2])
    driver = "HDF5" if version >= (3, 13) else "NETCDF"
    # Quoted URI is required when the signed URL includes query parameters.
    source = '{}:"/vsicurl/{}":{}'.format(driver, url, VAR)
    env = dict(
        GDAL_DISABLE_READDIR_ON_OPEN="YES",
        GDAL_HTTP_TIMEOUT="30",
        GDAL_HTTP_MAX_RETRY="2",
        GDAL_HTTP_RETRY_DELAY="1",
        GDAL_HTTP_MULTIPLEX="YES",
        GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
        CPL_VSIL_CURL_CHUNK_SIZE="262144",
        CPL_VSIL_CURL_CACHE_SIZE="67108864",
        CPL_CURL_VERBOSE="NO",
    )
    try:
        with rasterio.Env(**env):
            with rasterio.open(source) as ds:
                if not ds.crs or ds.count == 0:
                    raise RuntimeError("Missing CRS or raster band")
                bounds = transform_bounds("EPSG:4326", ds.crs, *AOI)
                w = from_bounds(*bounds, transform=ds.transform)
                w = w.round_offsets().round_lengths()
                w = w.intersection(Window(0, 0, ds.width, ds.height))
                if w.width < 2 or w.height < 2:
                    raise RuntimeError("AOI outside raster")
                if w.width > MAX_SRC_SIDE or w.height > MAX_SRC_SIDE:
                    raise RuntimeError("Native AOI larger than safety bound")
                raw = ds.read(1, window=w, masked=True)
                src_power = np.asarray(raw.filled(np.nan), dtype=np.float32)
                src_power[~np.isfinite(src_power) | (src_power <= 0)] = np.nan
                src_transform = ds.window_transform(w)
                native_crs = str(ds.crs)
    except Exception as exc:
        # GDAL exceptions can contain the signed URL: NEVER print exception text.
        raise RuntimeError("Remote GCOV extraction failed ("+
                           type(exc).__name__+"); see ASF GDAL guidance") from None

    dst_transform, width, height = target
    out_power = np.full((height, width), np.nan, dtype=np.float32)
    reproject(
        source=src_power,
        destination=out_power,
        src_transform=src_transform,
        src_crs=native_crs,
        src_nodata=np.nan,
        dst_transform=dst_transform,
        dst_crs=CRS,
        dst_nodata=np.nan,
        resampling=Resampling.nearest,
        num_threads=1,
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        out_db = 10.0*np.log10(out_power)
    out_db[~np.isfinite(out_db)] = np.nan
    if int(np.isfinite(out_db).sum()) < 200:
        raise RuntimeError("Too few valid aligned radar pixels in AOI")
    return out_db.astype(np.float32), {
        "date": date, "granule_id": gid, "processor": "P05036",
        "collection": COLLECTION, "band": VAR, "native_crs": native_crs,
        "native_window_shape": list(src_power.shape),
        "valid_aligned_pixels": int(np.isfinite(out_db).sum()),
        "median_db": round(float(np.nanmedian(out_db)), 4),
    }

def changes(before, after):
    import numpy as np
    if before.shape != after.shape:
        raise ValueError("Date rasters have different shapes")
    valid = np.isfinite(before) & np.isfinite(after)
    delta = np.full(before.shape, np.nan, dtype=np.float32)
    delta[valid] = after[valid] - before[valid]
    if not np.any(valid):
        raise ValueError("No shared valid pixels")
    vals = delta[valid]
    return delta, {
        "shared_valid_pixels": int(valid.sum()),
        "delta_db_median": round(float(np.median(vals)), 4),
        "delta_db_p10": round(float(np.percentile(vals, 10)), 4),
        "delta_db_p90": round(float(np.percentile(vals, 90)), 4),
        "meaning": "After minus before HHHH dB, not classified flood extent",
    }

def save_raster(path, data, target):
    import numpy as np
    import rasterio
    tf, width, height = target
    with rasterio.open(path, "w", driver="GTiff", width=width, height=height,
                       count=1, dtype="float32", crs=CRS, transform=tf,
                       nodata=np.nan, compress="deflate") as dst:
        dst.write(np.asarray(data, dtype=np.float32), 1)

def preview(before, after, delta):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
        for ax, arr, title, bounds in zip(
            axes, [before, after, delta],
            ["NISAR 29 Oct — HHHH dB", "NISAR 10 Nov — HHHH dB", "Change: after − before (dB)"],
            [(-27, 0), (-27, 0), (-8, 8)]):
            im = ax.imshow(np.ma.masked_invalid(arr), vmin=bounds[0],
                           vmax=bounds[1], cmap="viridis" if ax != axes[2] else "coolwarm")
            ax.set_title(title); ax.axis("off")
            fig.colorbar(im, ax=ax, shrink=0.8)
        fig.suptitle("Backscatter — Kuttanad NISAR GCOV V1; no flood labels")
        fig.savefig(OUT/"nisar_hhhh_comparison.png", dpi=150)
        plt.close(fig)
    except ImportError:
        print("matplotlib unavailable; map PNG skipped")

def self_test():
    import numpy as np
    a = np.array([[0.01, 0.1], [0.05, np.nan]], dtype=np.float64)
    b = np.array([[0.02, 0.1], [0.025, np.nan]], dtype=np.float64)
    before, after = 10*np.log10(a), 10*np.log10(b)
    delta, stats = changes(before, after)
    assert stats["shared_valid_pixels"] == 3
    assert abs(float(delta[0, 0])-3.01029996) < 0.001
    assert abs(float(delta[1, 0])+3.01029996) < 0.001
    assert np.isnan(delta[1, 1])
    print("PASS: difference/invalid-pixel mathematics")

def main():
    if "--self-test" in sys.argv:
        self_test(); return
    records = [discover(d) for d in DATES]
    for date, (gid, _) in zip(DATES, records):
        print(date, gid)
    if "--preflight" in sys.argv:
        print("PASS: both validated acquisition records found; no protected data accessed")
        return
    token = getpass.getpass("NASA Earthdata token (hidden; never saved): ").strip()
    if token.count(".") != 2:
        raise SystemExit("Invalid-looking Earthdata bearer token")
    target = make_grid()
    arrays, provenance = [], []
    for date, (gid, source) in zip(DATES, records):
        try:
            url = signed_url(source, token)
            print(date+": authenticated; extracting a small aligned AOI ...", flush=True)
            data, record = extract_one(date, gid, url, target)
        except Exception as exc:
            print(date+": "+str(exc) if type(exc) is RuntimeError
                  else date+": error of type "+type(exc).__name__)
            raise SystemExit(1) from None
        arrays.append(data); provenance.append(record)
        print(date+": "+str(record["valid_aligned_pixels"])+
              " valid grid pixels; median "+str(record["median_db"])+" dB")
    del token
    delta, summary = changes(*arrays)
    OUT.mkdir(parents=True, exist_ok=True)
    for date, data in zip(DATES, arrays):
        save_raster(OUT/("nisar_"+date+"_hhhh_db.tif"), data, target)
    save_raster(OUT/"nisar_delta_hhhh_db.tif", delta, target)
    preview(arrays[0], arrays[1], delta)
    doc = {
        "study_area_bbox_lonlat": AOI, "validated_collection": COLLECTION,
        "target_crs": CRS, "target_resolution_m": RESOLUTION_M,
        "observations": provenance, "difference": summary,
        "not_established": [
            "NISAR-derived water or flood classification",
            "agreement with OPERA, measurement accuracy, ground truth",
            "causal attribution or flood damage",
        ],
    }
    (OUT/"nisar_pair_summary.json").write_text(json.dumps(doc, indent=2)+"\n")
    print("Saved aligned radar rasters, change image and summary in:", OUT)
    print("The backscatter difference is not yet a validated inundation map.")

if __name__ == "__main__":
    main()
