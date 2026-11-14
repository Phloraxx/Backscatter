/** Deterministic interpretation of measured SAR signal and separate OPERA classes.
 * This is intentionally neither AI inference nor flood classification.
 */
export const getOpClass = (v) => ({
  0:'Non-water',
  1:'Open water',
  2:'Partial water (HLS)',
  3:'Inundated vegetation (S1)',
  250:'HAND masked',
  251:'Layover/shadow masked',
  252:'Snow/ice masked',
  253:'Cloud/shadow masked',
  254:'Ocean mask',
  255:'No data',
}[v] ?? 'Unknown / masked');

export const dbValue = (v) => Number.isFinite(v) ? v.toFixed(2) + ' dB' : 'No valid reading';
export const signedDbValue = (v) => Number.isFinite(v) ? (v >= 0 ? '+' : '') + v.toFixed(2) + ' dB' : 'No valid paired reading';

export function explainPixel(selected, assam) {
  if (!selected) return null;
  const valid = Number.isFinite(selected.a) && Number.isFinite(selected.b);
  const change = valid ? selected.b - selected.a : NaN;
  let radar;
  if (!valid) {
    radar = 'At least one radar acquisition lacks a valid sample here. No radar change can be determined.';
  } else if (Math.abs(change) < 3) {
    radar = 'HH radar return changed by ' + signedDbValue(change) + '. This is below the fixed ±3 dB strong-change threshold; it does not prove the surface was unchanged.';
  } else {
    const direction = change > 0 ? 'increased' : 'decreased';
    radar = 'HH radar return ' + direction + ' by ' + Math.abs(change).toFixed(2) + ' dB. This is a strong single-pixel signal difference, not a water or flood detection. The separate signal-cluster overlay also requires neighboring evidence.';
  }
  const status = getOpClass(selected.reference);
  const refUnavailable = selected.reference == null || selected.reference >= 250 || status.startsWith('Unknown');
  const reference = refUnavailable
    ? 'The displayed OPERA reference pixel is masked or unavailable; it cannot confirm a water class.'
    : 'OPERA classified this sample as ' + status.toLowerCase() + ' at its reference observation date. This is a satellite product, not field-confirmed water or flooding.';
  const timing = assam
    ? 'OPERA Sentinel-1D is from 31 Oct, three days after the first NISAR pass. The 10 Nov reference used for study-wide comparison is not the layer shown here.'
    : 'OPERA Sentinel-2B is from 29 Oct, the first NISAR date. The 05 Nov reference used for study-wide comparison is not the layer shown here.';
  return {radar, reference, timing, status, valid};
}

export function formatEvidenceReport({selected, meta, study}) {
  if (!selected || !meta) return '';
  const result = explainPixel(selected, study === 'assam');
  const name = study === 'assam' ? 'Lower Assam' : 'Kuttanad';
  const dates = meta.primary_dates ?? [];
  return [
    'BACKSCATTER — SATELLITE RADAR EVIDENCE NOTE',
    '==========================================',
    'Study: ' + name,
    'Sample location (WGS84): ' + selected.lat.toFixed(6) + '°, ' + selected.lng.toFixed(6) + '°',
    'NISAR HHHH ' + (dates[0] ?? 'unknown') + ': ' + dbValue(selected.a),
    'NISAR HHHH ' + (dates[1] ?? 'unknown') + ': ' + dbValue(selected.b),
    'Signed HHHH difference: ' + signedDbValue(selected.delta),
    ...(study === 'assam' ? [] : [
      'NISAR HVHV ' + (dates[0] ?? 'unknown') + ': ' + dbValue(selected.hvA),
      'NISAR HVHV ' + (dates[1] ?? 'unknown') + ': ' + dbValue(selected.hvB),
      'Signed HVHV difference: ' + signedDbValue(selected.hvDelta),
    ]),
    'OPERA WTR ' + (meta.opera_date ?? 'unknown') + ': ' + result.status,
    'Reference product: ' + (meta.opera_product ?? 'unknown'),
    '',
    'RADAR INTERPRETATION',
    result.radar,
    '',
    'REFERENCE AND TIMING',
    result.reference,
    result.timing,
    '',
    'PROVENANCE',
    'NISAR validated GCOV V1 / NASA–ISRO; NASA OPERA DSWx (ASF/Earthdata/PO.DAAC).',
    'Scientific source manifest: ' + (meta.source_manifest ?? 'not provided'),
    'Radar dates: ' + dates.join(' / '),
    'Source grid: ' + meta.pixel_width_m + ' × ' + meta.pixel_height_m + ' m (aligned to OPERA).',
    '',
    'LIMITATIONS',
    'This note reports satellite measurements, not field-confirmed flood extent.',
    'A dark pixel or strong HH difference does not uniquely imply flooding.',
    'Single-date OPERA labels cannot verify a between-date causal water transition.',
    'Calibration differences and non-contemporaneous reference imagery may affect interpretation.',
    'No AI flood model or calibrated flood probability is used.',
    '',
    'https://backscatter-afterimage-2026.pages.dev/research.html',
    '',
  ].join('\n');
}
