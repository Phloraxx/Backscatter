#!/usr/bin/env python3
"""Check Earthdata access to selected NISAR and OPERA datasets without full downloads (v3).

A NASA Earthdata bearer token is read securely at run time. The token is never
written to disk, printed, or sent to anything other than NASA's download hosts.
"""
import getpass
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import (HTTPRedirectHandler, Request, build_opener)

CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
BBOX = "76.42,9.40,76.49,9.47"  # selected Kuttanad region
NISAR_COLLECTION = "C2854338529-ASF"
DSWX_COLLECTION = "C2949811996-POCLOUD"

# Only permit NASA-hosted download redirects and these exact observed storage hosts.
ALLOWED_HOSTS = {
    "d1mv8zhcvry6x4.cloudfront.net",
    # Exact CDN host observed in PO.DAAC OPERA data redirects.
    "deotb6e7tfubr.cloudfront.net",
    # PO.DAAC distributes its protected OPERA files through this AWS S3 host.
    "podaac-ops-cumulus-protected.s3.us-west-2.amazonaws.com",
}


def nasa_host(host):
    return bool(host and (host.endswith(".nasa.gov") or
                          host.endswith(".earthdatacloud.nasa.gov") or
                          host in ALLOWED_HOSTS))


class NASAOnlyRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != "https" or not nasa_host(parsed.hostname):
            # Print only the destination hostname, not a signed URL or token.
            raise ValueError(
                f"Refusing redirect to an unrecognized host: {parsed.hostname}"
            )
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        # Credentials must never leave the NASA authentication service's
        # controlled hosts. A PO.DAAC CDN redirect uses its signed URL.
        if parsed.hostname in ALLOWED_HOSTS:
            for secret_header in ("Authorization", "Cookie", "Proxy-Authorization"):
                redirected.remove_header(secret_header)
            # Also remove any request-unredirected headers, if supplied.
            for secret_header in ("Authorization", "Cookie", "Proxy-Authorization"):
                redirected.unredirected_hdrs.pop(secret_header, None)
        return redirected


opener = build_opener(NASAOnlyRedirect())


def find_product(collection, date, pattern, suffix):
    query = {
        "collection_concept_id": collection,
        "bounding_box": BBOX,
        "temporal": f"{date}T00:00:00Z,{date}T23:59:59Z",
        "page_size": "100",
    }
    url = CMR + "?" + urlencode(query)
    with opener.open(Request(url), timeout=20) as response:
        records = json.load(response)["feed"]["entry"]
    candidates = [x for x in records if pattern in x.get("producer_granule_id", "")]
    if not candidates:
        return None
    item = candidates[0]
    urls = [x.get("href", "") for x in item.get("links", [])
            if x.get("href", "").startswith("https://") and
            x.get("href", "").endswith(suffix)]
    if not urls:
        return None
    file_url = urls[0]
    if not nasa_host(urlsplit(file_url).hostname):
        raise ValueError("Catalog returned an unexpected download host")
    return item["producer_granule_id"], file_url


def verify(token, label, item):
    if item is None:
        print(f"{label}: NO CATALOG MATCH")
        return
    product_name, url = item
    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Range": "bytes=0-4095",
        "User-Agent": "Backscatter-NISAR-feasibility-check/0.1",
    })
    try:
        with opener.open(req, timeout=35) as response:
            head = response.read(8)
            if url.endswith(".h5"):
                valid = head == b"\x89HDF\r\n\x1a\n"
            else:
                valid = head[:4] in (b"II*\x00", b"MM\x00*")
            print(f"{label}: HTTP {response.status}; "
                  f"valid file header: {valid}; "
                  f"content range: {response.headers.get('Content-Range', 'not provided')}")
    except HTTPError as e:
        print(f"{label}: HTTP {e.code}; "
              + ("authentication or authorization issue" if e.code in (401, 403)
                 else "server response"))
    except (URLError, ValueError) as e:
        print(f"{label}: error {type(e).__name__}: {str(e)[:120]}")
    print(f"  Granule: {product_name}")


def main():
    token = os.environ.get("EDL_TOKEN") or getpass.getpass("Earthdata bearer token (hidden): ").strip()
    if not token or token.count(".") != 2:
        raise SystemExit("No valid-looking Earthdata JWT was provided")
    print("Checking Kuttanad (Kerala) catalog products. Only small byte ranges requested.")
    tasks = [
        ("NISAR 2026-09-14", NISAR_COLLECTION, "2026-09-14", "_113_A_006_4005_DHDH_", ".h5"),
        ("NISAR 2026-09-26", NISAR_COLLECTION, "2026-09-26", "_113_A_006_4005_DHDH_", ".h5"),
        ("OPERA DSWx 2026-09-15", DSWX_COLLECTION, "2026-09-15", "_B01_WTR", "_B01_WTR.tif"),
        ("OPERA DSWx 2026-09-27", DSWX_COLLECTION, "2026-09-27", "_B01_WTR", "_B01_WTR.tif"),
    ]
    for label, collection, date, pattern, suffix in tasks:
        # OPERA filenames use a tile and a date; look for the water-band link.
        if collection == DSWX_COLLECTION:
            pattern = "OPERA_L3_DSWx-S1_"
        try:
            item = find_product(collection, date, pattern, suffix)
            verify(token, label, item)
        except Exception as exc:
            print(f"{label}: {type(exc).__name__}: {str(exc)[:120]}")


if __name__ == "__main__":
    main()
