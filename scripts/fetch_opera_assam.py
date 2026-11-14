#!/usr/bin/env python3
"""Download Lower Assam OPERA DSWx-S1 B01_WTR reference layers; no credentials saved.

NASA Earthdata token is read via getpass, never echoed or written to disk.
No inference: this program only retrieves authentic water-classification rasters.
"""
import getpass
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

COLLECTION = "C2949811996-POCLOUD"
CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
DATES = ("2026-10-31", "2026-11-10")
TILE = "_T46RBQ_"
OUT = Path.home() / "Downloads" / "backscatter-assam-validated" / "opera_s1"
HOSTS = {
    "deotb6e7tfubr.cloudfront.net",
    "podaac-ops-cumulus-protected.s3.us-west-2.amazonaws.com",
    "d1mv8zhcvry6x4.cloudfront.net",
}
LIMIT = 25 * 1024 * 1024

def is_nasa(host):
    return bool(host and host.endswith(".nasa.gov"))

class StrictRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        host = parsed.hostname
        if parsed.scheme != "https" or not (is_nasa(host) or host in HOSTS):
            raise ValueError("Unexpected redirect hostname: " + str(host))
        child = super().redirect_request(req, fp, code, msg, headers, newurl)
        if not is_nasa(host):
            for key in ("Authorization", "Cookie", "Proxy-Authorization"):
                child.remove_header(key)
                for actual in list(child.unredirected_hdrs):
                    if actual.lower() == key.lower():
                        child.unredirected_hdrs.pop(actual, None)
        return child

def discover():
    params = {
        "collection_concept_id": COLLECTION,
        "bounding_box": "90.20,26.16,90.60,26.22",
        "temporal": "2026-10-30T00:00:00Z,2026-11-11T23:59:59Z",
        "page_size": 250,
    }
    with build_opener(StrictRedirect()).open(CMR + "?" + urlencode(params), timeout=35) as resp:
        records = json.load(resp)["feed"]["entry"]
    chosen = []
    for item in records:
        name = item.get("producer_granule_id", "")
        if TILE not in name or not any(d.replace("-", "") in name for d in DATES):
            continue
        for link in item.get("links", []):
            url = link.get("href", "")
            if url.startswith("https://archive.podaac.earthdata.nasa.gov/") and url.endswith("_B01_WTR.tif"):
                chosen.append((name, item.get("time_start"), url))
                break
    if not chosen:
        raise RuntimeError("No Kuttanad WTR files found")
    return sorted(chosen)

def download(token):
    OUT.mkdir(parents=True, exist_ok=True)
    opener = build_opener(StrictRedirect())
    results = []
    for name, time_start, url in discover():
        filename = name + "_B01_WTR.tif"
        dest = OUT / filename
        if dest.is_file():
            data = dest.read_bytes()
        else:
            with opener.open(Request(url, headers={"Authorization": "Bearer " + token}), timeout=60) as r:
                data = r.read(LIMIT + 1)
            if len(data) > LIMIT:
                raise RuntimeError("Exceeded 25 MiB safety limit")
            if data[:4] not in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
                raise RuntimeError("Returned file was not TIFF")
            dest.write_bytes(data)
        r = {"acquired": time_start, "granule_id": name, "file": filename,
             "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
             "path": str(dest)}
        results.append(r)
        print("READY", name, "SIZE_BYTES", len(data), flush=True)
    (OUT / "wtr_manifest.json").write_text(json.dumps({
        "source": "NASA CMR OPERA DSWx-S1 v1.0", "collection": COLLECTION,
        "files": results,
        "warning": "Independent Sentinel-1 SAR water classification, not field ground truth",
    }, indent=2) + "\n")
    print("MANIFEST", OUT / "wtr_manifest.json")
    return results

def main():
    token = getpass.getpass("Earthdata bearer token (hidden): ").strip()
    if token.count(".") != 2:
        raise SystemExit("Invalid-looking token")
    try:
        download(token)
    except Exception as exc:
        # Don't print sensitive signed CDN URLs from HTTP exception details.
        print("ERROR_CLASS", type(exc).__name__)
        raise SystemExit(1) from None

if __name__ == "__main__":
    main()
