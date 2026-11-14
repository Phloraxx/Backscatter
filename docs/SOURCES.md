# Primary Research Sources

Prefer official sources for scientific/technical claims.

## NASA / NISAR
- https://science.nasa.gov/mission/nisar/
- https://science.nasa.gov/mission/nisar/about-the-satellite/
- https://science.nasa.gov/mission/nisar/mission-concept/
- https://science.nasa.gov/mission/nisar/mission-requirements/
- https://science.nasa.gov/mission/nisar/isro-partnership/
- https://science.nasa.gov/mission/nisar/polarimetry/

## ASF NISAR documentation
- https://nisar-docs.asf.alaska.edu/
- https://nisar-docs.asf.alaska.edu/availability-overview/
- https://nisar-docs.asf.alaska.edu/products-overview/
- https://nisar-docs.asf.alaska.edu/gunw/
- https://nisar-docs.asf.alaska.edu/phase/
- https://nisar-docs.asf.alaska.edu/harmony/
- https://nisar-docs.asf.alaska.edu/vertex/
- https://nisar-docs.asf.alaska.edu/earthaccess/
- https://nisar-docs.asf.alaska.edu/provisional-known-issues/

## ISRO
- https://www.isro.gov.in/
- Search ISRO for current NISAR S-band data release / Bhoonidhi documentation.

## NASA Space Apps
- https://www.spaceappschallenge.org/2026/challenges/
- https://www.spaceappschallenge.org/resources/

## Source policy

Do not cite this file as authority. Follow the links and verify the current official text before using a claim in the final presentation.

## Independent OPERA water reference documentation

- OPERA DSWx-HLS product specification: https://d2pn8kiwq2w21t.cloudfront.net/documents/OPERA_DSWx-HLS_ProductSpec_v1.0.0_D-107395_RevB.pdf
- OPERA water product suite: https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/
- NASA Earthdata CMR: https://cmr.earthdata.nasa.gov/search/granules.json
- OPERA DSWx-HLS collection `C2617126679-POCLOUD`
- Reproducible reference tests: `research/kuttanad_validated_2026_10_11/INDEPENDENT_COMPARISON.md`


## Lower Assam source and calibration references

- [NASA CMR catalog](https://cmr.earthdata.nasa.gov/search/granules.json): source IDs in [Assam manifest](../research/assam_validated_2026_10_11/scene_manifest.json).
- [NISAR validated release notes](https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/): known pre-Nov-12 calibration issues.
- [OPERA DSWx-S1 classification codes](https://developers.google.com/earth-engine/datasets/catalog/OPERA_DSWX_L3_V1_S1): 0, 1, 3 and mask classes.

## Additional signal-filter sources

- [NISAR validated availability](https://nisar-docs.asf.alaska.edu/availability-overview/) — validated data begin October 21, 2026.
- [ASF NISAR maturity cautions](https://hyp3-docs.asf.alaska.edu/nisar-docs/products-overview/) — different processing maturities can cause artifacts when compared.
- [NASA JPL OPERA suite](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/) — DSWx-S1 and DSWx-HLS are not harmonized across sensors.
- [ASF calibrated release notes](https://hyp3-docs.asf.alaska.edu/nisar-docs/release-notes/) — some pre-November-12 acquisition modes have radiometric residuals.
- [Original Backscatter signal-coherence experiment](../research/signal_coherence/README.md) — fixed parameters, metrics, limitations and reproduction.


## Cyclone Arnab event evidence

- [IMD October 28 cyclone position/landfall bulletin](https://mausam.imd.gov.in/backend/assets/cyclone_pdf/10_Hourly_Bulletin_271026_2300UTC.pdf) — records landfall near 16.45°N 81.9°E.
- [International Charter activation 1056](https://disasterscharter.org/activations/flood-in-india-activation-1056-) — independently documents affected coastal districts and flood-response imagery.
- [NASA CMR-verified four-scene manifest](../research/arnab_event/scene_manifest.json) — exact dates, IDs, spacecraft and NISAR polygon checks; the separate **measured pixel results** are in [the Arnab report](../research/arnab_event/MEASURED_RESULTS.md).
- [NASA NISAR validated availability](https://nisar-docs.asf.alaska.edu/availability-overview/).
- [NASA OPERA DSWx suite](https://www.jpl.nasa.gov/go/opera/products/dswx-product-suite/).


## Public three-study research page

- [Backscatter public research and full method limitations](https://backscatter-afterimage-2026.pages.dev/research.html): all three measured cases, test results and actual source lineage, not confirmed flood extent.
- [Cyclone Arnab measured report](../research/arnab_event/MEASURED_RESULTS.md): original AOI, corrected T44QND source tile, reference date alignment, fixed-rules failure.
