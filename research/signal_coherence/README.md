# Backscatter — conservative radar signal-change experiment

**Study date:** 14 November 2026

**Team:** Afterimage

**Status:** Completed on real validated NASA–ISRO NISAR HHHH measurements for two regions. **Not a flood detector.**

## Decision

**Add an optional SIGNAL CLUSTERS layer to the evidence viewer, but do not label it as water or inundation.** It highlights strong, spatially consistent changes in the measured HH backscatter. The method reduces noisy signal alerts in Kuttanad, but fails to identify independently classified open-water transitions in Assam. This negative result is part of the submission evidence.

## Why we did not build a 3+ date validated baseline

The [validated NISAR collection](https://nisar-docs.asf.alaska.edu/availability-overview/) begins with L-band acquisitions on October 21, 2026. The November 14 NASA CMR search for *matching track/frame/geometry* found:

| Study | Matching validated GCOV HHHH dates |
|---|---|
| Kuttanad, Kerala | 2026-10-29, 2026-11-10 |
| Lower Assam | 2026-10-28, 2026-11-09 |

Other radar tracks may cover the same region but cannot safely be treated as repeat-view observations. Earlier *provisional* NISAR data exist, but the [ASF product documentation](https://hyp3-docs.asf.alaska.edu/nisar-docs/products-overview/) warns that comparisons between different maturity/processing levels may reflect processing differences instead of surface changes. A reliable *validated-only* three-date baseline is therefore unavailable for these exact tracks as of this research date.

## Predeclared methods: all operate on NISAR alone

First, aggregate real 10 m NISAR GCOV **linear power** to the relevant independent reference's 30 m grid and then compute \`10×log10(power)\`. This alignment was already implemented in the source experiments. **No OPERA WTR water labels are used in the change filter.**

The three fixed-parameter experiments are:

1. **RAW**: HH difference (after minus before) ≤−3 dB is radar *decrease*, and ≥+3 dB is radar *increase*.
2. **MEDIAN3**: apply a NaN-aware 3×3 median filter to *each date's dB image separately* (requiring at least 5 valid cells) and threshold the resulting difference at ±3 dB.
3. **COHERENT**: start from MEDIAN3 and keep only a changed cell with at least **6 same-sign strong-change neighbors out of 9** (including itself), and at least 7 common-valid neighbors.

The values **3 dB**, **3×3**, and **6-of-9** are engineering choices for a conservative visual filter. They were *not optimized on OPERA water-change labels*. They do **not represent a calibrated probability of flooding**. Filtering can also erase small or narrow real features.

A candidate **signal decrease** (teal) or **signal increase** (amber) is displayed. Radar changes can reflect water, vegetation, crops, roughness, wet soil, geometric effects or residual calibration variation. Neither signal direction is synonymous with water gain or loss.

## Comparison with OPERA: evaluation only

To learn what the methods miss or wrongly highlight, the *final outputs* were compared with OPERA reference classes **0=non-water** and **1=open water** on cells valid for both dates.

- **Kuttanad:** OPERA DSWx-HLS Sentinel-2B Oct 29, Sentinel-2A Nov 05. NISAR Oct 29 / Nov 10. **Five-day offset on the final comparison**. HLS partial water class 2 is excluded from strict binary metrics.
- **Lower Assam:** OPERA DSWx-S1 Sentinel-1 Oct 31 / Nov 10. NISAR Oct 28 / Nov 09. **+3/+1-day offsets**. S1 class 3 means *inundated vegetation*, is NOT HLS class 2, and is excluded from strict open-water F1.

NASA JPL explicitly states that its [OPERA DSWx product suite](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/) shares format and 30 m posting but **is not harmonized across the different sensors**. The Kuttanad/Assam scores below are not a common ground-truth accuracy benchmark. OPERA itself is an algorithmic satellite classification, not independent field observations.

### Kuttanad (OPERA HLS reference)

| Diagnostic | RAW | MEDIAN3 | COHERENT |
|---|---:|---:|---:|
| Potential strong radar-signal region | 12.1032 km² | 10.9143 km² | **8.1108 km²** |
| Shared radar area flagged | 20.270% | 18.279% | **13.584%** |
| OPERA 0→1 vs radar signal decrease: precision | 0.25358 | 0.38072 | **0.44225** |
| OPERA 0→1 vs radar signal decrease: recall | 0.52028 | **0.53566** | 0.40699 |
| OPERA 0→1 vs radar signal decrease: F1 | 0.34097 | **0.44509** | 0.42389 |
| OPERA 1→0 vs radar signal increase: F1 | 0.19966 | 0.22228 | **0.23905** |
| Fraction of OPERA-stable non-water highlighted (either direction) | 4.303% | 1.386% | **0.319%** |

**Meaning:** MEDIAN3 provided the best gain F1 among these three rules, whereas COHERENT cut the fraction of *reference-stable non-water* incorrectly highlighted by approximately **92.6% compared with RAW**, with reduced recall. This is a useful reduction in clutter for an evidence viewer—not established flood detection.

The **8.1108 km²** of coherent radar change may include crops, wetland vegetation, water, and other surfaces. It is **not a mapped flood area**.

### Lower Assam (OPERA S1 reference)

| Diagnostic | RAW | MEDIAN3 | COHERENT |
|---|---:|---:|---:|
| Strong radar-signal region | 4.1031 km² | 1.4751 km² | **0.4329 km²** |
| Shared radar area flagged | 7.518% | 2.703% | **0.793%** |
| OPERA 0→1 vs radar decrease: F1 | 0.00730 | 0.00238 | **0.00000** |
| OPERA 1→0 vs radar increase: F1 | 0.01520 | 0.00977 | **0.00000** |
| Fraction of OPERA-stable non-water highlighted | 7.003% | 2.668% | 0.860% |

**Meaning:** Strong spatial filtering reduced the amount of highlighted radar signal dramatically, but detected **none** of the strict reference-classified open-water gain/loss transitions in this case. It is not an improved water-change detector there. The observed pair may not capture a meaningful environmental water event, and inundated vegetation and agricultural variation are substantial confounds.

The **0.4329 km²** of coherent radar signal change is not an Assam flood-area estimate.

## Additional signal variability

| Quantity | Kuttanad | Lower Assam |
|---|---:|---:|
| Shared radar-valid 30 m cells | 66,343 | 60,640 |
| Strict 0/1 reference cells valid on both dates | 45,184 | 50,500 |
| Median raw HH difference (30 m, dB) | +0.51534 | +0.10118 |
| Median absolute deviation of raw difference (dB) | 1.24138 | 0.99769 |

These medians use coarsened *30 m* radar data. They differ from the earlier reported 10 m Kuttanad paired median +0.6231 dB due to resolution and masking. No error is implied.

## Robustness and limitations

- No learning/training is done here. This avoids direct label leakage, but cannot guarantee that prechosen thresholds generalize.
- Both inputs are from only two validated acquisitions per track, so we do not estimate an actual historical distribution of persistent surfaces.
- Adjacent 30 m cells are spatially correlated, and changed fields can be entire coherent blocks. Coherence is a spatial pattern, not a true-flood confidence score.
- Kuttanad and Assam use different OPERA reference products and acquisition-date gaps. A comparison of their F1 values does not isolate geography as the cause.
- Some NISAR acquisition modes before Nov 12, 2026 have [radiometric residuals around 1 dB](https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/). Whether these exact granules are affected is not yet confirmed. This is one reason to avoid interpreting marginal dB differences as physical change.
- No field-confirmed flood extent, water-change accuracy or affected-population/damage estimate is claimed.

## Reproduce from real source data

After retrieving original HHHH, HVHV, and OPERA water reference GeoTIFFs for both study regions and regenerating their native web rasters:

\`\`\`bash
python scripts/export_demo_assets.py
python scripts/export_assam_demo.py
python scripts/evaluate_signal_coherence.py
python scripts/check_web_assets.py
cd web && npm run build
\`\`\`

The signal experiment generates [Kuttanad JSON](kuttanad_metrics.json), [Assam JSON](assam_metrics.json), transparent \`web/public/data/coherent_change.png\` and \`web/public/data/assam/coherent_change.png\`. It also synchronizes scientific summary fields in each region's web \`meta.json\`. No Earthdata credential or raw source GeoTIFF is committed.

## Product decision

Display **SIGNAL CLUSTERS** as an optional overlay in the two-region website with explicit labels:

- **Teal:** strong spatially consistent radar **decrease**.
- **Amber:** strong spatially consistent radar **increase**.
- **No highlight:** unchanged, weak, incoherent or unsupported radar signal.
- **No flood interpretation assigned to any pixel.**

Improve future science by finding a **documented event** with better-matched before/after water reference data and additional validated same-track radar repeats after they become available. Use it as an independent test of water changes rather than optimizing the rule against the existing two cases.
