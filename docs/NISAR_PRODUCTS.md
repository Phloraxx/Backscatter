# NISAR Products Relevant to Backscatter

## GCOV

**Geocoded Polarimetric Covariance** is the leading MVP candidate.

Why:
- geocoded;
- calibrated;
- radiometrically terrain corrected;
- suited to backscatter analysis;
- appropriate for disturbance/inundation-related workflows.

Potential use:
- compare calibrated backscatter across compatible dates;
- derive differences / ratios;
- use polarization-dependent features;
- generate inundation-change candidates.

## GUNW

**Geocoded Unwrapped Interferogram** can provide interferometric information including coherence.

Potential use:
- supplementary evidence of surface change;
- advanced deformation modules later.

Risk:
- InSAR interpretation is significantly more difficult than backscatter change detection.

## GSLC

Useful for complex SAR workflows and advanced processing, but likely unnecessary for the first hackathon MVP.

## GOFF

Offset-tracking products may support displacement/motion use cases, but are not the first choice for flood/wetland MVP.

## Product policy

Start at the highest processing level that preserves the science needed for the MVP.

Do not process raw radar merely to appear technically sophisticated.

## Compatibility checks

Before comparing scenes, verify:
- spatial overlap;
- acquisition geometry;
- orbit/track/frame as required;
- polarization availability;
- product version;
- processing generation;
- temporal relationship;
- valid masks / nodata.
