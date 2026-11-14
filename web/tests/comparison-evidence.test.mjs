import {test} from 'node:test';
import assert from 'node:assert/strict';
import {clampSwipePercent, percentFromClientX, imageAffineCss} from '../src/comparison.js';
import {getOpClass, explainPixel, formatEvidenceReport, signedDbValue} from '../src/evidence.js';

const selected={
  lng:76.455, lat:9.435, a:-15, b:-10, delta:5,
  hvA:-18, hvB:-19, hvDelta:-1, reference:1,
};
const meta={
  primary_dates:['2026-10-29','2026-11-10'],opera_date:'2026-10-29',
  opera_product:'OPERA test original granule',source_manifest:'https://example.org/provenance',
  pixel_width_m:30,pixel_height_m:30,
};

test('swipe percent is clamped and handles invalid input',()=>{
  assert.equal(clampSwipePercent(-3),5);
  assert.equal(clampSwipePercent(150),95);
  assert.equal(clampSwipePercent(NaN),50);
  assert.equal(percentFromClientX(130,{left:100,width:200}),15);
  assert.equal(percentFromClientX(300,{left:100,width:200}),95);
  assert.equal(percentFromClientX(150,{left:100,width:0}),50);
});

test('affine georeferencing maps NW, NE and SW raster corners to projected pixels',()=>{
  assert.equal(imageAffineCss([{x:10,y:20},{x:110,y:20},{x:110,y:120},{x:10,y:120}],100,100),
    'matrix(1, 0, 0, 1, 10, 20)');
  assert.equal(imageAffineCss([],100,100),null);
  assert.equal(imageAffineCss([{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}],0,100),null);
});

test('OPERA partial water and inundated vegetation are distinct reference classes',()=>{
  assert.equal(getOpClass(0),'Non-water');
  assert.equal(getOpClass(1),'Open water');
  assert.equal(getOpClass(2),'Partial water (HLS)');
  assert.equal(getOpClass(3),'Inundated vegetation (S1)');
  assert.equal(getOpClass(251),'Layover/shadow masked');
});

test('strong HH signal never becomes a flood claim',()=>{
  const explanation=explainPixel(selected,false);
  assert.match(explanation.radar,/strong single-pixel signal difference, not a water or flood detection/i);
  assert.match(explanation.reference,/satellite product, not field-confirmed/i);
  assert.match(explanation.timing,/05 Nov/);
  assert.equal(explanation.valid,true);
});

test('weak HH signal does not establish a physically unchanged surface',()=>{
  const out=explainPixel({...selected,b:-14},false);
  assert.match(out.radar,/below the fixed ±3 dB/i);
  assert.match(out.radar,/does not prove the surface was unchanged/i);
});

test('invalid or masked reference observations cannot be described as open water',()=>{
  const out=explainPixel({...selected,reference:255},true);
  assert.match(out.reference,/masked or unavailable/);
  assert.match(out.timing,/three days after/);
  const invalid=explainPixel({...selected,b:NaN},true);
  assert.match(invalid.radar,/No radar change can be determined/);
});

test('exported evidence includes actual dates, both polarizations and source metadata',()=>{
  const note=formatEvidenceReport({selected,meta,study:'kuttanad'});
  assert.match(note,/2026-10-29/);
  assert.match(note,/2026-11-10/);
  assert.match(note,/Signed HVHV difference: -1.00 dB/);
  assert.match(note,/OPERA test original granule/);
  assert.match(note,/https:\/\/example.org\/provenance/);
  assert.match(note,/not field-confirmed flood extent/);
  assert.match(note,/No AI flood model/);
});

test('Assam evidence never fabricates unavailable HV measurements',()=>{
  const note=formatEvidenceReport({selected,meta:{...meta,opera_date:'2026-10-31'},study:'assam'});
  assert.match(note,/Lower Assam/);
  assert.doesNotMatch(note,/HVHV/);
  assert.match(note,/31 Oct, three days after/);
  assert.equal(formatEvidenceReport({selected:null,meta,study:'assam'}),'');
});

test('dB display preserves sign and missing values',()=>{
  assert.equal(signedDbValue(0),'+0.00 dB');
  assert.equal(signedDbValue(-0.1),'-0.10 dB');
  assert.equal(signedDbValue(NaN),'No valid paired reading');
});
