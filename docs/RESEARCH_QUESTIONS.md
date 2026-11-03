# Open Research Questions

High-priority questions to answer with real data:

1. Which 2026 NISAR GCOV observations provide the strongest compatible Kerala/India scene pairs?
2. Is there a significant flood/wetland event inside those acquisition windows?
3. Which polarization products are available for those scenes?
4. What water-change signal is visible in dB?
5. How much does adaptive thresholding outperform a fixed threshold?
6. Does GUNW coherence add useful information for the selected case?
7. What independent dataset can validate the mask?
8. How stable is the classifier on a second region?
9. What false positives dominate?
10. What is the minimum processing needed for a judge to trust the result?

## Research rule

Answer these experimentally. Do not make architecture decisions from assumptions when a small data test can decide the issue.


## Progress as of 2026-11-03

- Q1 scene discovery: **partial yes** — compatible metadata for Kuttanad NISAR Sep 14/26, with authenticated file headers.
- Q2 meaningful event / observed SAR change: **unknown** — OPERA shows classified water change; no NISAR interpretation yet.
- Q3 polarization: naming indicates DHDH; internal measured layer availability and meaning require HDF5 inspection.
- Q7 independent comparison data: **yes for availability** — OPERA DSWx-S1 WTR Sep 15/27 acquired and inspected; not ground truth.
- Remaining questions require actual NISAR measurement arrays and validation.
