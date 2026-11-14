#!/usr/bin/env python3
"""Verify a preselected Cyclone Arnab before/after NISAR and OPERA pair.

The AOI was fixed before processing pixels: 81.82–81.89 E, 16.58–16.65 N,
near the documented Oct 28, 2026 landfall in coastal Andhra Pradesh.

Checks product concept IDs, acquisition dates, matching NISAR mode, source
download-link existence, and both NISAR footprint polygons containing all
four selected study corners. No Earthdata credentials or protected files
are required. Does NOT verify flood extent or the local event at pixel level.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

CMR = "https://cmr.earthdata.nasa.gov/search/granules.json"
AOI = [81.82,16.58,81.89,16.65]
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "arnab_event"
ITEMS = [
  dict(type="nisar", id="G4405748574-ASF", day="2026-10-22",
       collection="C3622241360-ASF", asset=".h5"),
  dict(type="nisar", id="G4405145629-ASF", day="2026-11-03",
       collection="C3622241360-ASF", asset=".h5"),
  dict(type="opera-s1", id="G4386072092-POCLOUD", day="2026-10-23",
       collection="C2949811996-POCLOUD", asset="_B01_WTR.tif"),
  dict(type="opera-s1", id="G4405822836-POCLOUD", day="2026-11-04",
       collection="C2949811996-POCLOUD", asset="_B01_WTR.tif"),
]
CORNERS=[(AOI[0],AOI[1]),(AOI[0],AOI[3]),(AOI[2],AOI[1]),(AOI[2],AOI[3])]

def inside(x,y,polygon):
    selected=False
    for i in range(len(polygon)-1):
        x1,y1=polygon[i];x2,y2=polygon[i+1]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:
            selected=not selected
    return selected

def polygon_points(record):
    geometry=record.get("polygons",[])
    if not geometry or not geometry[0]:return []
    values=[float(k) for k in geometry[0][0].split()]
    return [(values[i+1],values[i]) for i in range(0,len(values),2)]

def get_record(item):
    q={"concept_id":item["id"],"page_size":2}
    with urlopen(CMR+"?"+urlencode(q),timeout=30) as response:
        v=json.load(response)["feed"]["entry"]
    if len(v)!=1 or v[0].get("id")!=item["id"]:
        raise RuntimeError("CMR ID missing: "+item["id"])
    row=v[0]
    timestamp=row.get("time_start","")
    name=row.get("producer_granule_id","")
    if not timestamp.startswith(item["day"]):
        raise RuntimeError("Unexpected acquisition day: "+item["id"])
    links=[u["href"] for u in row.get("links",[]) if
           u.get("href","").startswith("https://") and
           u.get("href","").endswith(item["asset"])]
    if not links:
        raise RuntimeError("Granule has no expected source asset: "+item["id"])
    if item["type"]=="nisar":
        if "_149_D_080_4005_DHDH_" not in name or "_P05036_" not in name:
            raise RuntimeError("NISAR mode or CRID mismatch: "+item["id"])
        polygon=polygon_points(row)
        if not polygon or not all(inside(*pt,polygon) for pt in CORNERS):
            raise RuntimeError("NISAR footprint does not contain full AOI")
    else:
        if "_T44QPD_" not in name or "_S1D_30_v1.0" not in name:
            raise RuntimeError("Unexpected OPERA tile / source sensor")
    return {
        "source":item["type"],"collection":item["collection"],
        "concept_id":item["id"],"granule":name,
        "acquired_utc":timestamp,
        "CMR_metadata_verified":True,
        "source_asset_exists_in_catalog":True,
        "nisar_full_footprint_contains_AOI":True if item["type"]=="nisar" else None,
    }

def main():
    records=[get_record(item) for item in ITEMS]
    intervals=[]
    for i in (0,1):
        n=datetime.fromisoformat(records[i]["acquired_utc"].replace("Z","+00:00"))
        o=datetime.fromisoformat(records[i+2]["acquired_utc"].replace("Z","+00:00"))
        intervals.append(round((o-n).total_seconds()/3600,4))
    manifest={
      "status":"CATALOG VERIFIED ONLY; no Arnab-region NISAR or OPERA pixel analysis at time of manifest creation",
      "event":"Cyclone Arnab, 28 Oct 2026, coastal Andhra Pradesh",
      "event_evidence":"IMD landfall near 16.45N,81.9E, International Charter activation 1056",
      "aoi_wgs84_lonlat":AOI,
      "aoi_preselected_before_pixel_inspection":True,
      "nisar_observations":["2026-10-22","2026-11-03"],
      "opera_s1_observations":["2026-10-23","2026-11-04"],
      "opera_minus_nisar_hours":intervals,
      "polarization":"NISAR frequencyA HHHH",
      "harmony_variable_id":"V4137651715-ASF",
      "output_crs":"EPSG:32644",
      "same_acquisition_geometry":"149_D_080_4005_DHDH",
      "calibration_crid":"P05036",
      "opera_tile":"T44QPD","opera_sensor":"Sentinel-1D C-band",
      "products":records,
      "limitations":[
        "Even nearly time-matched OPERA S1 is a satellite classification, not field truth",
        "This is an event contextual AOI, not proof of flooding in every pixel",
        "The NISAR and OPERA radar frequencies, incidence and classifications differ",
        "Calibration residuals can affect some NISAR acquisitions before Nov 12 2026; scene-specific status is unverified",
        "Only two same-track validated NISAR dates available; do not create a fictitious historical baseline",
        "Charter/ISRO flood map is background evidence, not a pixel-level ground truth label for this exact box"
      ],
      "official_sources":{
        "charter":"https://disasterscharter.org/activations/flood-in-india-activation-1056-",
        "india_meteorological_department":"https://mausam.imd.gov.in/backend/assets/cyclone_pdf/10_Hourly_Bulletin_271026_2300UTC.pdf",
        "nisar_availability":"https://nisar-docs.asf.alaska.edu/availability-overview/",
        "nisar_known_issues":"https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/"
      }
    }
    OUT.mkdir(parents=True,exist_ok=True)
    p=OUT/"scene_manifest.json"
    p.write_text(json.dumps(manifest,indent=2)+"\n")
    for row in records:
        print("VERIFIED",row["source"],row["acquired_utc"],row["concept_id"])
    print("TIME_GAPS_HOURS",intervals)
    print("SUCCESS: four source products and both NISAR footprints confirmed; pixels NOT analyzed")
    print("MANIFEST",p)

if __name__=="__main__":
    main()
