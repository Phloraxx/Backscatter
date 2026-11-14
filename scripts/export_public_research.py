#!/usr/bin/env python3
"""Generate the public, read-only Backscatter research page from measured JSON.

Run after evaluating all three cases; commits no Earthdata credentials or raw TIFFs.
The public viewer remains two selectable studies; Cyclone Arnab is a separate
event-linked scientific test, not a verified flood map.
"""
import json
import shutil
from pathlib import Path
from html import escape

ROOT=Path(__file__).resolve().parent.parent
PUBLIC=ROOT/"web"/"public"
ASSETS=PUBLIC/"research"
K=ROOT/"research"/"signal_coherence"/"kuttanad_metrics.json"
A=ROOT/"research"/"signal_coherence"/"assam_metrics.json"
C=ROOT/"research"/"arnab_event"/"arnab_nisar_opera_diagnostic.json"
FIG=ROOT/"research"/"arnab_event"/"arnab_radar_change.jpg"
SIGNAL=ROOT/"research"/"arnab_event"/"arnab_coherent_signal.png"

def load(p):
    if not p.is_file():raise FileNotFoundError(p)
    return json.loads(p.read_text())

def f(v,d=3):
    if v is None:return "—"
    return format(float(v),f".{d}f")

def run():
    k,a,c=load(K),load(A),load(C)
    assert c["strict_class0_1_both_cells"]>=1000
    assert c["sources"]["opera_granules"][0].startswith("OPERA_L3_DSWx-S1_T44QND_")
    assert c["sources"]["opera_granules"][1].startswith("OPERA_L3_DSWx-S1_T44QND_")
    assert c["reference_hour_offsets"]==[11.2031,11.2025]
    assert (c["fixed_signal_methods_without_opera_training"]["coherent"]
            ["water_gain_vs_radar_decrease"]["f1"])==0.0
    for p in (FIG,SIGNAL):
        assert p.is_file(),p
    ASSETS.mkdir(parents=True,exist_ok=True)
    for src,target in [(FIG,"arnab-radar-change.jpg"),(SIGNAL,"arnab-signal.png"),
                       (K,"kuttanad-coherence.json"),(A,"assam-coherence.json"),
                       (C,"arnab-metrics.json"),
                       (ROOT/"research"/"arnab_event"/"scene_manifest.json","arnab-manifest.json")]:
        shutil.copy2(src,ASSETS/target)

    k_raw=k["methods"]["raw"]["reference_diagnostic"]["stable_nonwater_flag_fraction"]*100
    k_coh=k["methods"]["coherent"]["reference_diagnostic"]["stable_nonwater_flag_fraction"]*100
    a_coh=a["methods"]["coherent"]["reference_diagnostic"]
    c_fixed=c["fixed_signal_methods_without_opera_training"]["coherent"]
    gain=c_fixed["water_gain_vs_radar_decrease"]
    loss=c_fixed["water_loss_vs_radar_increase"]
    html=f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#111a1b"><title>Backscatter · Research, methods and limitations</title>
<link rel="icon" href="/brand/favicon.png">
<style>
:root{{color-scheme:dark;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:#0d1517;color:#e9efe7}}
*{{box-sizing:border-box}}body{{margin:0}}a{{color:#e0c68e}}header{{padding:18px max(22px,calc((100vw - 1100px)/2));background:#101b1d;border-bottom:1px solid #405453;display:flex;align-items:center;gap:16px}}header img{{width:53px;height:53px;object-fit:contain;background:#fff;border-radius:9px;padding:3px}}header b{{letter-spacing:.09em}}header nav{{margin-left:auto;display:flex;gap:16px;font-size:13px;flex-wrap:wrap}}main{{max-width:1100px;margin:auto;padding:34px 22px 70px}}h1{{font-size:clamp(32px,4vw,52px);letter-spacing:-.04em;margin:12px 0}}h2{{font-size:28px;letter-spacing:-.02em;margin-top:42px}}h3{{font-size:19px;margin:0 0 10px}}p,li{{line-height:1.65;color:#c4d0c9}}.intro{{font-size:20px;max-width:890px}}.eyebrow{{font-size:12px;text-transform:uppercase;color:#dbc58b;letter-spacing:.2em}}.warn{{border-left:3px solid #c9a260;background:#182424;padding:17px 19px;line-height:1.5;color:#ecdaba;margin:22px 0}}.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:24px}}.card{{padding:22px;border-radius:10px;background:#172426;border:1px solid #314847}}.card .num{{font-size:34px;color:#e5cd91;font-weight:750;letter-spacing:-.03em;margin:15px 0 5px}}.tag{{font-size:11px;color:#8ccece;letter-spacing:.1em;text-transform:uppercase}}.small{{font-size:13px}}table{{border-collapse:collapse;width:100%;margin:20px 0}}td,th{{padding:13px 15px;border-bottom:1px solid #334747;text-align:left}}th{{color:#e5cd91;font-size:12px;letter-spacing:.08em}}img.figure{{max-width:100%;width:100%;border-radius:8px;border:1px solid #34494b;background:white}}.split{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}.pill{{border:1px solid #485b53;border-radius:30px;display:inline-block;padding:8px 13px;font-size:12px;color:#e4d3a2;margin:7px 7px 7px 0}}.source{{font-size:12px;line-height:1.6}}footer{{border-top:1px solid #344747;padding:25px 22px;font-size:12px;text-align:center;color:#a0b4aa}}
@media(max-width:740px){{.cards,.split{{display:block}}.card{{margin:13px 0}}header{{flex-wrap:wrap}}header nav{{margin:5px 0 0 0;width:100%}}td,th{{padding:10px 8px;font-size:12px}}}}
</style></head><body>
<header><img src="/brand/backscatter-mark.png" alt="Original Backscatter logo"><div><b>BACKSCATTER</b><div class="small">Team Afterimage · NASA Space Apps 2026</div></div>
<nav><a href="/">Interactive map</a><a href="/backscatter-demo.pdf">Seven-slide PDF</a></nav></header>
<main><div class="eyebrow">Real NASA satellite data · openly documented tests</div>
<h1>Observe first.<br>Interpret carefully.</h1>
<p class="intro">Backscatter compares actual NASA–ISRO NISAR radar measurements, contextual NASA OPERA water-classification products, and fixed, reproducible signal-change methods. The central research finding is a limitation: <strong>a change in radar backscatter does not necessarily mean flooding.</strong></p>
<div class="warn"><strong>Important:</strong> None of these studies provides field-validated flood extent, flood prediction, public warnings, affected-population counts, or reliable pixel-level water-change accuracy. The figures below measure agreement with satellite-derived OPERA classifications recorded on different acquisition dates.</div>
<h2>Three measured case studies</h2>
<div class="cards">
<div class="card"><div class="tag">01 · Kerala · Interactive</div><h3>Kuttanad</h3><div class="num">{f(k_coh,3)}%</div><div>OPERA-classified stable non-water falsely flagged by the coherent signal filter, versus {f(k_raw,3)}% with raw ±3 dB change.</div><p class="small">Denoising improves visual selectivity but does not validate flooding. NISAR: Oct 29 / Nov 10; OPERA DSWx-HLS reference includes a five-day later-date mismatch.</p><a href="/research/kuttanad-coherence.json">Measured JSON</a></div>
<div class="card"><div class="tag">02 · Assam · Interactive</div><h3>Lower Assam</h3><div class="num">{f(a_coh["water_gain_vs_radar_decrease"]["f1"])}</div><div>Coherent radar-decrease vs OPERA new-open-water F1; gain and loss both zero in this study.</div><p class="small">NISAR: Oct 28 / Nov 09; reference OPERA DSWx-S1: Oct 31 / Nov 10. Sentinel-1 WTR class 3 means inundated vegetation.</p><a href="/research/assam-coherence.json">Measured JSON</a></div>
<div class="card"><div class="tag">03 · Andhra Pradesh · Event test</div><h3>Cyclone Arnab</h3><div class="num">{f(gain["f1"])}</div><div>Fixed coherent radar-decrease vs OPERA new-open-water F1, despite the documented October 28 cyclone.</div><p class="small">NISAR: Oct 22 / Nov 03; reference OPERA DSWx-S1: Oct 23 / Nov 04, each ≈11.2 hours later. The rule also scored zero for open-water loss.</p><a href="/research/arnab-metrics.json">Measured JSON</a></div>
</div>
<h2>Cyclone Arnab: a stronger, independent event test</h2>
<p>IMD confirmed landfall on October 28, 2026, near 16.45°N, 81.9°E. We selected a 7-km-scale Godavari-delta area north of the reported landfall before inspecting its radar pixels. NISAR and OPERA provide matching before-and-after acquisitions approximately 11.2 hours apart. Actual OPERA references use <strong>Sentinel-1 tile T44QND</strong>; a neighboring tile found by the catalog was rejected once its georeferenced raster bounds proved it did not overlap the selected area.</p>
<img class="figure" src="/research/arnab-radar-change.jpg" alt="Real validated NISAR HHHH maps of October 22 and November 3, plus their measured backscatter difference. Not a flood map.">
<div class="split">
<div><h3 style="margin-top:22px">What the water reference says</h3><p>In 58,085 comparable 30 m cells, OPERA's separate Sentinel-1 classification changed from non-water to open water in <strong>{c["reference_gain_cells"]:,} cells</strong> and from open water to non-water in <strong>{c["reference_loss_cells"]:,} cells</strong>. These are reference-class transitions, not confirmed cyclone-caused flood area.</p></div>
<div><h3 style="margin-top:22px">What the unchanged HH radar rule found</h3><p>The fixed 3 dB / 3×3 median / 6-of-9 coherent radar rule captured <strong>{gain["tp"]} out of {c["reference_gain_cells"]:,} new-open-water cells</strong> and <strong>{loss["tp"]} out of {c["reference_loss_cells"]:,} lost-open-water cells</strong>. Its highlighted {f(c_fixed["candidate_signal_area_km2"],4)} km² is <strong>radar-signal change, not flood extent</strong>.</p></div>
</div>
<h2>What the methods actually do</h2>
<table><thead><tr><th>Method</th><th>Radar signal only (no water labels)</th><th>Known limit</th></tr></thead><tbody>
<tr><td>RAW</td><td>Signed 30 m HHHH radar difference ≥±3 dB.</td><td>Speckle, crops, geometry and calibration variation.</td></tr>
<tr><td>MEDIAN3</td><td>3×3 median separately per date; compare afterward.</td><td>Can erase small/narrow genuine features.</td></tr>
<tr><td>COHERENT</td><td>MEDIAN3 with ≥6/9 neighbors changing the same direction.</td><td>Coherent land-cover changes need not be water changes.</td></tr>
<tr><td>OPERA reference</td><td>Independent satellite water-classification product.</td><td>Not field truth; reference times and sensors differ.</td></tr>
</tbody></table>
<p>The Arnab locally fitted static-water classifier scored F1 <strong>{f(c["first_reference_east_test"]["f1"],4)}</strong> in a spatial holdout, but its reference water-gain F1 was only <strong>{f(c["candidate_gain_agreement"]["f1"],4)}</strong>. A good single-date classification is not the same as good change detection.</p>
<div class="warn">NISAR scenes acquired before November 12, 2026 may contain mode-specific radiometric residuals. The affected status of these exact scenes was not established; the observed median scene change of {f(c["median_nisar_delta_db"],4)} dB cannot be confidently attributed to floodwater.</div>
<h2>Source documentation and reproducibility</h2>
<a class="pill" href="/research/arnab-metrics.json">Arnab result JSON</a><a class="pill" href="/research/arnab-manifest.json">Four source granules</a><a class="pill" href="/research/kuttanad-coherence.json">Kuttanad experiment</a><a class="pill" href="/research/assam-coherence.json">Assam experiment</a>
<p class="source">Primary data: NASA–ISRO NISAR Level-2 validated GCOV (via ASF/Earthdata), NASA OPERA DSWx-HLS / DSWx-S1 (via PO.DAAC). Event context: <a href="https://mausam.imd.gov.in/Forecast/mcmarq/mcmarq_data/Press%20Release%20Dtd%2028.10.2026.pdf">India Meteorological Department</a> and <a href="https://disasterscharter.org/activations/flood-in-india-activation-1056-">International Charter activation 1056</a>. Data/product caveats: <a href="https://nisar-docs.asf.alaska.edu/availability-overview/">NISAR</a> and <a href="https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/">ASF known issues</a>. The team's original logo appears above. No Earthdata credentials or raw TIFFs are present on this public website.</p>
</main><footer>Backscatter · Afterimage · NASA Space Apps Challenge 2026 · Evidence, not flood predictions</footer></body></html>"""
    path=PUBLIC/"research.html"
    path.write_text(html)
    print("PUBLIC_RESEARCH_GENERATED",path,"SIZE",path.stat().st_size,
          "ASSET_COUNT",len(list(ASSETS.iterdir())))
    print("COHERENT_GAIN_F1",gain["f1"],"LOSS_F1",loss["f1"])

if __name__=="__main__":
    run()
