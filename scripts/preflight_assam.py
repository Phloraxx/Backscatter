#!/usr/bin/env python3
"""Public-metadata check for a *candidate* second Backscatter study in Lower Assam.

No Earthdata bearer token or protected file download is needed. Run:
  python scripts/preflight_assam.py
Only catalog compatibility is verified, never radar pixels or flood extent.
"""
import json
from urllib.parse import urlencode
from urllib.request import urlopen

CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
BOX = "90.28,26.16,90.35,26.23"

ITEMS = [
    dict(source="NISAR validated GCOV", collection="C3622241360-ASF",
         day="2026-10-28", expected="NISAR_L2_PR_GCOV_034_069_A_015_4005_DHDH_A_20261028T232206_20261028T232240_P05036_N_F_J_001",
         asset=".h5"),
    dict(source="NISAR validated GCOV", collection="C3622241360-ASF",
         day="2026-11-09", expected="NISAR_L2_PR_GCOV_035_069_A_015_4005_DHDH_A_20261109T232206_20261109T232241_P05036_N_F_J_001",
         asset=".h5"),
    dict(source="OPERA DSWx-S1 WTR", collection="C2949811996-POCLOUD",
         day="2026-10-31", expected="OPERA_L3_DSWx-S1_T46RBQ_20261031T235432Z_20261101T200652Z_S1D_30_v1.0",
         asset="_B01_WTR.tif"),
    dict(source="OPERA DSWx-S1 WTR", collection="C2949811996-POCLOUD",
         day="2026-11-10", expected="OPERA_L3_DSWx-S1_T46RBQ_20261110T120427Z_20261110T210338Z_S1D_30_v1.0",
         asset="_B01_WTR.tif"),
]

def find(item):
    params = {
        "collection_concept_id": item["collection"],
        "bounding_box": BOX,
        "temporal": item["day"]+"T00:00:00Z,"+item["day"]+"T23:59:59Z",
        "page_size": "100",
    }
    with urlopen(CMR+"?"+urlencode(params), timeout=30) as response:
        data = json.load(response)["feed"]["entry"]
    matches = [g for g in data if g.get("producer_granule_id") == item["expected"]]
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one matching catalog product: "+
                           item["expected"])
    granule = matches[0]
    links = [link.get("href", "") for link in granule.get("links", [])
             if link.get("href", "").startswith("https://") and
             link.get("href", "").endswith(item["asset"])]
    if not links:
        raise RuntimeError("Matching product has no expected download asset")
    return granule.get("id"), len(links)

def main():
    print("Lower Assam, India, candidate bbox:", BOX)
    for item in ITEMS:
        concept, assets = find(item)
        print("FOUND", item["day"], item["source"],
              "concept", concept, "assets", assets)
    print("PASS: source catalog availability only; authenticated pixels remain untested")
    print("REFERENCE DATE GAPS: +3 days (Oct 28→Oct 31), +1 day (Nov 09→Nov 10)")
    print("WARNING: ASF documents potential pre-Nov-12 radiometric residuals in certain radar modes.")
    print("NO claims of inundation extent, flood damage, change accuracy, or usable pixel overlap.")

if __name__ == "__main__":
    main()
