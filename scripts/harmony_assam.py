#!/usr/bin/env python3
"""Retrieve validated NISAR HHHH over Lower Assam as an independent case study.

Usage:
  python scripts/harmony_extra_layers.py submit
  python scripts/harmony_extra_layers.py fetch

Requires local Earthdata token via getpass, not CLI arguments or saved config.
Creates 2 small processing requests: HHHH for each NISAR
date. Reuses existing jobs, and securely downloads only finished TIFFs.
Does not label a radar pixel as water/flooded.
"""
import getpass
import json
import sys
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

ROOT = Path.home() / "Downloads" / "backscatter-assam-validated"
OUT = ROOT / "nisar"
HARMONY = "https://harmony.earthdata.nasa.gov"
COLLECTION = "C3622241360-ASF"
GRANULES = {
    "2026-10-28": "G4410147621-ASF",
    "2026-11-09": "G4409018076-ASF",
}
LAYERS = {
    "HHHH": "V4137651715-ASF",
}
CDN_HOSTS = {"dqzb5lcolc8fj.cloudfront.net"}
MAX_BYTES = 30 * 1024 * 1024

class SecureRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = urlsplit(newurl).hostname
        if urlsplit(newurl).scheme != "https" or not (
            host and (host.endswith(".nasa.gov") or host in CDN_HOSTS)
        ):
            raise ValueError("Unexpected redirect hostname")
        child = super().redirect_request(req, fp, code, msg, headers, newurl)
        if host in CDN_HOSTS:
            for key in ("Authorization", "Cookie", "Proxy-Authorization"):
                child.remove_header(key)
                for original in list(child.unredirected_hdrs):
                    if original.lower() == key.lower():
                        child.unredirected_hdrs.pop(original, None)
        return child

def open_json(opener, url, token):
    if urlsplit(url).scheme != "https" or urlsplit(url).hostname != "harmony.earthdata.nasa.gov":
        raise ValueError("Unexpected API hostname")
    req = Request(url, headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
    with opener.open(req, timeout=50) as response:
        return json.load(response)

def job_path(date, layer):
    return OUT / ("job_" + date + "_" + layer + ".json")

def tiff_path(date, layer):
    return OUT / ("nisar_" + date + "_" + layer + ".tif")

def submission_url(date, layer):
    params = [
        ("granuleId", GRANULES[date]),
        ("variable", LAYERS[layer]),
        ("subset", "lon(90.28:90.35)"),
        ("subset", "lat(26.16:26.23)"),
        ("outputCrs", "EPSG:32646"),
        ("format", "image/tiff"),
        ("forceAsync", "true"),
        ("skipPreview", "true"),
        ("maxResults", "1"),
        ("label", "backscatter-assam-" + date + "-" + layer),
    ]
    return (HARMONY + "/" + COLLECTION +
            "/ogc-api-coverages/1.0.0/collections/parameter_vars/coverage/rangeset?" +
            urlencode(params))

def run(action, token):
    OUT.mkdir(parents=True, exist_ok=True)
    opener = build_opener(SecureRedirect())
    records = []
    for date in GRANULES:
        for layer in LAYERS:
            path = job_path(date, layer)
            if action == "submit":
                if path.exists() and json.loads(path.read_text()).get("jobID"):
                    print("EXISTING", date, layer)
                    continue
                obj = open_json(opener, submission_url(date, layer), token)
                job_id = obj.get("jobID")
                if not job_id:
                    raise RuntimeError("No Harmony job ID")
                path.write_text(json.dumps({"jobID": job_id, "date": date,
                    "layer": layer, "granule_id": GRANULES[date],
                    "variable_id": LAYERS[layer]}, indent=2) + "\n")
                print("SUBMITTED", date, layer, "STATUS", obj.get("status"), flush=True)
                continue

            if not path.exists():
                print("MISSING_JOB", date, layer)
                continue
            job_id = json.loads(path.read_text())["jobID"]
            job = open_json(opener, HARMONY + "/jobs/" + job_id, token)
            status = job.get("status")
            records.append({"date": date, "layer": layer, "job": job_id,
                            "status": status, "progress": job.get("progress")})
            dest = tiff_path(date, layer)
            print("JOB", date, layer, "STATUS", status, "PROGRESS", job.get("progress"), flush=True)
            if status != "successful" or dest.exists():
                continue
            hrefs = [x["href"] for x in job.get("links", []) if
                     x.get("rel") == "data" and
                     urlsplit(x.get("href", "")).path.lower().endswith(".tif")]
            if len(hrefs) != 1 or urlsplit(hrefs[0]).hostname != "harmony.earthdata.nasa.gov":
                raise RuntimeError("Expected one trusted data TIFF link")
            req = Request(hrefs[0], headers={"Authorization": "Bearer " + token})
            with opener.open(req, timeout=60) as response:
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES or data[:4] not in (
                b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+"
            ):
                raise RuntimeError("Output failed size/TIFF verification")
            dest.write_bytes(data)
            print("DOWNLOADED", dest.name, len(data), "bytes", flush=True)
    if action == "fetch":
        (OUT / "status.json").write_text(json.dumps(records, indent=2) + "\n")
    return records

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("submit", "fetch"):
        raise SystemExit("Usage: python harmony_assam.py [submit|fetch]")
    token = getpass.getpass("Earthdata bearer token (hidden): ").strip()
    if token.count(".") != 2:
        raise SystemExit("Invalid-looking Earthdata token")
    try:
        run(sys.argv[1], token)
    except Exception as e:
        # Error details from HTTP may reveal a signed download URL. Do not echo.
        print("ERROR_CLASS", type(e).__name__)
        raise SystemExit(1) from None

if __name__ == "__main__":
    main()
