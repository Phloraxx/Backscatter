# SAR / NISAR Science Context

## SAR basics

Synthetic Aperture Radar is an active remote-sensing technique. The satellite transmits microwave energy and measures the signal scattered back toward the sensor.

The measured backscatter depends on factors including:
- surface roughness;
- dielectric properties / moisture;
- geometry;
- vegetation structure;
- wavelength;
- polarization.

## Why SAR matters

Unlike optical imagery, radar observations are not dependent on sunlight and are substantially less limited by cloud cover. This makes SAR especially useful during storms and monsoon periods when optical imagery may be obscured.

## NISAR

NISAR is the NASA–ISRO Synthetic Aperture Radar mission.

Important conceptual properties:
- L-band radar from NASA;
- S-band radar from ISRO;
- repeated observations enabling change analysis;
- products designed for ecosystem, solid-earth, cryosphere and hydrology applications.

## Backscatter and water

Smooth open water often reflects radar energy away from the sensor, producing relatively low backscatter. However:
- wind can roughen water;
- emergent/flooded vegetation can increase or alter scattering;
- urban flooding behaves differently;
- incidence angle matters;
- terrain/shadow can confound interpretation.

Therefore a simple global threshold is not scientifically sufficient.

## Coherence

Interferometric coherence measures similarity of the radar scattering behavior between acquisitions.

Low coherence can indicate meaningful surface change, but also:
- vegetation movement;
- temporal decorrelation;
- geometric mismatch;
- noise;
- acquisition differences.

Treat coherence as evidence, not a direct semantic label.

## dB representation

Backscatter power is commonly converted to decibels:

`dB = 10 * log10(power)`

Never apply logarithms without masking zero/invalid/nodata values.

## Core scientific principle

Backscatter should expose the measurements behind each interpretation and avoid claiming certainty the data cannot support.
