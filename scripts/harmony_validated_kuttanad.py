#!/usr/bin/env python3
"""Reproducible NASA Harmony extraction of two validated NISAR GCOV HHHH subsets.

Python >=3.9, standard library only. Token entered via getpass; never logged/stored.
Commands:
  python scripts/harmony_validated_kuttanad.py submit
  python scripts/harmony_validated_kuttanad.py fetch
Submit creates two Harmony processing jobs; fetch inspects their state and
downloads successful small GeoTIFFs to ~/Downloads/backscatter-validated-kuttanad.
No flood classification. No need to download 5GB source HDF5s.
"""
import getpass
import json
import sys
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

OUT = Path.home() / "Downloads" / "backscatter-validated-kuttanad"
BASE = "https://harmony.earthdata.nasa.gov"
COLLECTION = "C3622241360-ASF"
HHHH_VARIABLE = "V4137651715-ASF"  # /science/LSAR/GCOV/grids/frequencyA/HHHH
GRANULES = {
    "2026-10-29": "G4404626243-ASF",
    "2026-11-10": "G4409682460-ASF",
}
KNOWN_CDNS = {"dqzb5lcolc8fj.cloudfront.net"}
MAX_BYTES = 30 * 1024 * 1024


class TrustedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, url):
        u = urlsplit(url)
        if (u.scheme != "https" or not u.hostname or
                not (u.hostname.endswith(".nasa.gov") or u.hostname in KNOWN_CDNS)):
            raise ValueError("Untrusted HTTPS redirect hostname: " + str(u.hostname))
        child = super().redirect_request(req, fp, code, msg, headers, url)
        if not u.hostname.endswith(".nasa.gov"):
            for secret in ("Authorization", "Cookie", "Proxy-Authorization"):
                child.remove_header(secret)
                for original in list(child.unredirected_hdrs):
                    if original.lower() == secret.lower():
                        child.unredirected_hdrs.pop(original)
        return child


def open_json(opener, url, token):
    if urlsplit(url).scheme != "https" or urlsplit(url).hostname != "harmony.earthdata.nasa.gov":
        raise ValueError("Unexpected API hostname")
    request = Request(url, headers={"Authorization": "Bearer " + token,
                                    "Accept": "application/json"})
    with opener.open(request, timeout=45) as response:
        return json.load(response)


def submission(date, granule):
    query = [
        ("granuleId", granule), ("variable", HHHH_VARIABLE),
        ("subset", "lon(76.42:76.49)"), ("subset", "lat(9.40:9.47)"),
        ("outputCrs", "EPSG:32643"), ("format", "image/tiff"),
        ("forceAsync", "true"), ("skipPreview", "true"),
        ("maxResults", "1"), ("label", "backscatter-kuttanad-" + date),
    ]
    return (BASE + "/" + COLLECTION +
            "/ogc-api-coverages/1.0.0/collections/parameter_vars/coverage/rangeset?"
            + urlencode(query))


def job_file(date):
    return OUT / ("harmony_submission_" + date + ".json")


def submit(opener, token):
    for date, granule in GRANULES.items():
        path = job_file(date)
        if path.exists() and json.loads(path.read_text()).get("jobID"):
            print(date, "existing Harmony job; not resubmitting")
            continue
        response = open_json(opener, submission(date, granule), token)
        if not response.get("jobID"):
            raise RuntimeError("Harmony did not issue a job ID")
        path.write_text(json.dumps({"jobID": response["jobID"],
                                    "status_at_submission": response.get("status")}, indent=2) + "\n")
        print(date, "submitted; status", response.get("status"))


def fetch(opener, token):
    for date in GRANULES:
        path = job_file(date)
        if not path.exists():
            print(date, "no job ID; run submit first")
            continue
        jid = json.loads(path.read_text())["jobID"]
        status = open_json(opener, BASE + "/jobs/" + jid, token)
        print(date, "status", status.get("status"), "progress", status.get("progress"))
        if status.get("status") != "successful":
            continue
        dest = OUT / ("nisar_" + date + "_hhhh_raw.tif")
        if dest.exists():
            print(date, "GeoTIFF already exists:", dest.name)
            continue
        hrefs = [x.get("href", "") for x in status.get("links", [])
                 if x.get("rel") == "data" and urlsplit(x.get("href", "")).path.lower().endswith(".tif")]
        if len(hrefs) != 1:
            # Do not accidentally download a wrong layer or silently choose one.
            print(date, "expected one HHHH GeoTIFF data link, found", len(hrefs))
            continue
        href = hrefs[0]
        if urlsplit(href).hostname != "harmony.earthdata.nasa.gov":
            raise ValueError("Unexpected Harmony output host")
        req = Request(href, headers={"Authorization": "Bearer " + token})
        with opener.open(req, timeout=60) as response:
            data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES or data[:4] not in (
                b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"):
            raise RuntimeError("Unexpected or non-TIFF Harmony output")
        dest.write_bytes(data)
        print(date, "downloaded", len(data), "bytes:", dest.name)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("submit", "fetch"):
        raise SystemExit("Usage: python harmony_validated_kuttanad.py [submit|fetch]")
    OUT.mkdir(parents=True, exist_ok=True)
    token = getpass.getpass("Earthdata token (hidden): ").strip()
    if token.count(".") != 2:
        raise SystemExit("Invalid-looking token")
    opener = build_opener(TrustedRedirect())
    try:
        if sys.argv[1] == "submit":
            submit(opener, token)
        else:
            fetch(opener, token)
    except Exception as exc:
        # Hide raw HTTP/GDAL exception messages: URLs may contain signed parameters.
        print("Harmony workflow error:", type(exc).__name__)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
