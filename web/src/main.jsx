import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import * as maplibregl from 'maplibre-gl';
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import proj4 from 'proj4';
import {imageAffineCss, percentFromClientX, clampSwipePercent} from './comparison.js';
import {explainPixel, formatEvidenceReport, getOpClass} from './evidence.js';
import 'maplibre-gl/dist/maplibre-gl.css';
import './styles.css';

maplibregl.setWorkerUrl(maplibreWorkerUrl);
proj4.defs('EPSG:32643', '+proj=utm +zone=43 +datum=WGS84 +units=m +no_defs');
proj4.defs('EPSG:32646', '+proj=utm +zone=46 +datum=WGS84 +units=m +no_defs');
const STUDY = new URLSearchParams(window.location.search).get('study') === 'assam' ? 'assam' : 'kuttanad';
const ASSAM = STUDY === 'assam';
const DATA_ROOT = ASSAM ? '/data/assam/' : '/data/';
const dateLabel = (date) => date ? new Date(date+'T12:00:00Z').toLocaleDateString('en-GB',{day:'numeric',month:'short',timeZone:'UTC'}) : '—';
const signedDb = (v) => Number.isFinite(v) ? (v>=0?'+':'')+v.toFixed(2) : '—';

const LAYERS = ASSAM ? [
  { id:'oct29', label:'28 OCT', detail:'NISAR · before', file:'before.png' },
  { id:'nov10', label:'09 NOV', detail:'NISAR · after', file:'after.png' },
  { id:'compare', label:'SWIPE COMPARE', detail:'28 Oct ↔ 09 Nov · HH', file:null },
  { id:'change', label:'RADAR CHANGE', detail:'HH · 09 Nov − 28 Oct', file:'change.png' },
  { id:'signal', label:'SIGNAL CLUSTERS', detail:'Coherent HH changes · NOT flood', file:'coherent_change.png' },
  { id:'opera', label:'OPERA WATER', detail:'Sentinel-1 · 31 Oct', file:'opera.png' },
] : [
  { id:'oct29', label:'29 OCT', detail:'NISAR · before', file:'oct29.png' },
  { id:'nov10', label:'10 NOV', detail:'NISAR · after', file:'nov10.png' },
  { id:'compare', label:'SWIPE COMPARE', detail:'29 Oct ↔ 10 Nov · HH', file:null },
  { id:'change', label:'RADAR CHANGE', detail:'HH · 10 Nov − 29 Oct', file:'change.png' },
  { id:'signal', label:'SIGNAL CLUSTERS', detail:'Coherent HH changes · NOT flood', file:'coherent_change.png' },
  { id:'hvchange', label:'HV CHANGE', detail:'HV · 10 Nov − 29 Oct', file:'hv_change.png' },
  { id:'opera', label:'OPERA WATER', detail:'Sentinel-2 · 29 Oct', file:'opera_oct29.png' },
];

const getDb = (v) => Number.isFinite(v) ? v.toFixed(2) + ' dB' : 'No valid reading';
function Legend({mode}) {
  if (mode === 'compare') return (
    <div className="legend-row comparison-legend">
      <span><i className="dot before-dot"/>Left: first NISAR pass</span>
      <span><i className="dot after-dot"/>Right: second NISAR pass</span>
    </div>
  );
  if (mode === 'opera') return (
    <div className="legend-row"><span><i className="dot water"/>Open water</span><span><i className="dot partial"/>{ASSAM?'Inundated vegetation':'Partial water'}</span><span><i className="dot land"/>Non-water</span><span><i className="dot invalid"/>Masked</span></div>
  );
  if (mode === 'signal') return (
    <div className="legend-row">
      <span><i className="dot signal-down"/>HH signal decrease</span>
      <span><i className="dot signal-up"/>HH signal increase</span>
    </div>
  );
  if (mode === 'change' || mode === 'hvchange') return (
    <div className="legend-heat"><span>−8 dB</span><div className="bar difference"/><span>+8 dB</span></div>
  );
  return <div className="legend-heat"><span>−27 dB</span><div className="bar strength"/><span>0 dB</span></div>;
}

function App() {
  const [meta,setMeta] = useState(null);
  const [buffer,setBuffer] = useState(null);
  const [error,setError] = useState('');
  const [mode,setMode] = useState('change');
  const [opacity,setOpacity] = useState(0.88);
  const [comparePos,setComparePos] = useState(50);
  const [selected,setSelected] = useState(null);
  const [mapReady,setMapReady] = useState(false);
  const mapRef = useRef(null);
  const pinRef = useRef(null);
  const mapNode = useRef(null);
  const swipeImageRef = useRef(null);

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch(DATA_ROOT+'meta.json').then(r=>{if(!r.ok)throw new Error('Missing dataset metadata');return r.json();}),
      fetch(DATA_ROOT+'pixels.bin').then(r=>{if(!r.ok)throw new Error('Missing measurement data');return r.arrayBuffer();}),
    ]).then(([m,b]) => {if(active){setMeta(m);setBuffer(b);}}).catch(e=>{if(active)setError(e.message);});
    return ()=>{active=false};
  }, []);

  useEffect(() => {
    if(!meta || !buffer || !mapNode.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapNode.current,
      center: ASSAM ? [90.315,26.195] : [76.455,9.435],
      zoom: 12.7,
      pitch: 0,
      minPitch: 0, maxPitch: 0,
      dragRotate: false, touchPitch: false,
      attributionControl: false,
      style: {
        version: 8,
        sources: {
          carto: {type:'raster',tiles:['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],tileSize:256,
            attribution:'© OpenStreetMap contributors'},
        },
        layers: [{id:'basemap',source:'carto',type:'raster'}],
      },
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({showCompass:false}), 'bottom-right');
    map.addControl(new maplibregl.AttributionControl({compact:true}), 'bottom-left');
    const len = meta.rows*meta.cols;
    if(buffer.byteLength !== 17*len){setError('Measurement grid has an unexpected size');map.remove();mapRef.current=null;return;}
    const before = new Float32Array(buffer,0,len);
    const after = new Float32Array(buffer,4*len,len);
    const hvBefore = new Float32Array(buffer,8*len,len);
    const hvAfter = new Float32Array(buffer,12*len,len);
    const optical = new Uint8Array(buffer,16*len,len);
    const lngs=meta.image_coordinates_lonlat.map(x=>x[0]);
    const lats=meta.image_coordinates_lonlat.map(x=>x[1]);
    const alignSwipeImage=()=>{
      const img=swipeImageRef.current;
      if(!img) return;
      const pts=meta.image_coordinates_lonlat.map(c=>map.project(c));
      const transform=imageAffineCss(pts,meta.cols,meta.rows);
      if(transform) img.style.transform=transform;
    };
    map.on('move',alignSwipeImage);
    map.on('resize',alignSwipeImage);
    map.on('load', () => {
      for(const layer of LAYERS.filter(l=>l.file)){
        map.addSource('image-'+layer.id,{type:'image',url:DATA_ROOT+layer.file,
          coordinates:meta.image_coordinates_lonlat});
        map.addLayer({id:'layer-'+layer.id,source:'image-'+layer.id,type:'raster',
          layout:{visibility:layer.id==='change'?'visible':'none'},
          paint:{'raster-opacity':opacity,'raster-resampling':'nearest'}});
      }
      map.fitBounds([[Math.min(...lngs),Math.min(...lats)],[Math.max(...lngs),Math.max(...lats)]],
        {padding:{top:100,bottom:95,left:65,right:65},duration:0,maxZoom:15});
      setMapReady(true);
      alignSwipeImage();
    });
    map.on('click',(e) => {
      const [x,y]=proj4('EPSG:4326',meta.crs,[e.lngLat.lng,e.lngLat.lat]);
      const col=Math.floor((x-meta.x0)/meta.pixel_width_m);
      const row=Math.floor((meta.y0-y)/meta.pixel_height_m);
      if(col<0 || row<0 || col>=meta.cols || row>=meta.rows){
        setSelected(null);
        if(pinRef.current){pinRef.current.remove();pinRef.current=null;}
        return;
      }
      const i=row*meta.cols+col;
      const a=before[i],b=after[i], hvA=hvBefore[i], hvB=hvAfter[i];
      setSelected({lng:e.lngLat.lng,lat:e.lngLat.lat,a,b,hvA,hvB,
        hvDelta:Number.isFinite(hvA)&&Number.isFinite(hvB)?hvB-hvA:NaN,
        delta:Number.isFinite(a)&&Number.isFinite(b)?b-a:NaN,
        reference:optical[i]});
      if(pinRef.current)pinRef.current.remove();
      pinRef.current=new maplibregl.Marker({color:'#f6ca74',scale:0.8})
        .setLngLat(e.lngLat).addTo(map);
    });
    map.on('error', e => {if(e?.error?.message?.includes('Failed to fetch')) setError('Map tiles could not load. Check your internet connection.');});
    return () => {
      if(pinRef.current)pinRef.current.remove();
      pinRef.current=null;
      map.remove();
      mapRef.current=null;
      setMapReady(false);
    };
  },[meta,buffer]);

  useEffect(()=>{
    const map=mapRef.current;
    if(!map || !mapReady) return;
    for(const layer of LAYERS.filter(l=>l.file)){
      if(map.getLayer('layer-'+layer.id)){
        const show=mode===layer.id || (mode==='compare' && layer.id==='oct29');
        map.setLayoutProperty('layer-'+layer.id,'visibility',show?'visible':'none');
        map.setPaintProperty('layer-'+layer.id,'raster-opacity',mode==='compare'?1:opacity);
      }
    }
  },[mode,opacity,mapReady]);

  useEffect(()=>{
    const map=mapRef.current;
    if(mode!=='compare'||!mapReady||!meta||!map||!swipeImageRef.current) return;
    const pts=meta.image_coordinates_lonlat.map(c=>map.project(c));
    const transform=imageAffineCss(pts,meta.cols,meta.rows);
    if(transform)swipeImageRef.current.style.transform=transform;
  },[mode,mapReady,meta]);

  const changeSwipePosition=(e)=>{
    const rect=mapNode.current?.getBoundingClientRect();
    setComparePos(percentFromClientX(e.clientX,rect));
  };
  const saveEvidenceNote=()=>{
    if(!selected||!meta)return;
    const text=formatEvidenceReport({selected,meta,study:STUDY});
    const blob=new Blob([text],{type:'text/plain;charset=utf-8'});
    const url=URL.createObjectURL(blob);
    const link=document.createElement('a');
    link.href=url;
    link.download='backscatter-'+STUDY+'-'+selected.lat.toFixed(4)+'-'+selected.lng.toFixed(4)+'.txt';
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(()=>URL.revokeObjectURL(url),3000);
  };
  const explanation=selected?explainPixel(selected,ASSAM):null;
  const active=LAYERS.find(l=>l.id===mode);
  return (
    <div className="shell">
      <div className="map-canvas" ref={mapNode} role="region" aria-label={"Interactive NISAR radar image map of "+(ASSAM?"Lower Assam":"Kuttanad")}/>
      <div className="map-grain" aria-hidden="true"/>
      {mode==='compare' && mapReady && meta && <div className="swipe-visual" aria-hidden="true">
        <div className="swipe-reveal" style={{clipPath:'inset(0 0 0 '+comparePos+'%)'}}>
          <img ref={swipeImageRef} className="swipe-image" src={DATA_ROOT+(ASSAM?'after.png':'nov10.png')}
            width={meta.cols} height={meta.rows} alt=""/>
        </div>
      </div>}
      <header className="top-bar">
        <a className="brand-mark" href="/brand/backscatter-original.png" target="_blank" rel="noreferrer" aria-label="View our original Backscatter globe-and-radar logo"><img src="/brand/backscatter-mark.png" alt="Backscatter globe-and-radar mark"/></a>
        <div className="identity">
          <div className="wordmark">BACKSCATTER<span className="tiny-star">✳</span></div>
          <div className="subheading">RADAR EVIDENCE FOR A CHANGING EARTH</div>
        </div>
        <div className="mission">
          <span className="live-dot"/>NASA SPACE APPS 2026 <span className="mission-sep">/</span> AFTERIMAGE
        </div>
        <a className="deck-link" href="/backscatter-demo.pdf" target="_blank" rel="noopener noreferrer" aria-label="Open Backscatter seven-slide NASA Space Apps demo PDF">7-SLIDE DEMO ↗</a>
      </header>

      <main className="workspace">
        <section className="control-panel">
          <nav className="study-switch" aria-label="Select satellite study area">
            <a className={!ASSAM?'selected':''} href="/?study=kuttanad" aria-current={!ASSAM?'page':undefined}>01 / KUTTANAD</a>
            <a className={ASSAM?'selected':''} href="/?study=assam" aria-current={ASSAM?'page':undefined}>02 / ASSAM</a>
          </nav>
          <div className="overline"><span className="overline-line"/> FIELD STUDY {ASSAM?'02':'01'} <span className="overline-faint">/ {ASSAM?'ASSAM':'KERALA'}, INDIA</span></div>
          <h1>{ASSAM?'Lower Assam':'Kuttanad'} <em>through radar.</em></h1>
          <p className="intro">{ASSAM
            ? 'A second independent test: the same radar-darkness rule does not transfer reliably from Kerala. Inspect the measurements, not a claimed flood map.'
            : 'See what NASA–ISRO NISAR measured between two observations. Explore changing radar signals without confusing them with confirmed flood extents.'}</p>
          <div className="scene-meta"><span>{ASSAM?'26.20° N, 90.31° E':'09.43° N, 76.45° E'}</span><span className="bullet">·</span><span>10 m source radar</span></div>
          <div className="panel-rule"/>
          <div className="panel-label">OBSERVATION LAYERS</div>
          <div className="layer-options" role="group" aria-label="Choose observation layer">
            {LAYERS.map((layer,i)=><button key={layer.id} type="button"
              className={'layer-option '+(mode===layer.id?'active':'')}
              onClick={()=>setMode(layer.id)} aria-pressed={mode===layer.id}>
              <span className="layer-index">0{i+1}</span>
              <span className="layer-title"><strong>{layer.label}</strong><small>{layer.detail}</small></span>
              <span className="layer-indicator">{mode===layer.id?'●':'○'}</span>
            </button>)}
          </div>
          <div className="opacity">
            {mode==='compare' ? <>
              <div className="opacity-caption"><span>SWIPE DIVIDER</span><output>{Math.round(comparePos)}% left</output></div>
              <input type="range" min="5" max="95" value={Math.round(comparePos)}
                onChange={e=>setComparePos(clampSwipePercent(Number(e.target.value)))}
                aria-label="Before after comparison position" />
              <p className="compare-hint">Drag the divider on the map or use this slider. Both radar images are displayed at full strength; neither shows flood extent.</p>
            </> : <>
              <div className="opacity-caption"><span>OVERLAY OPACITY</span><output>{Math.round(opacity*100)}%</output></div>
              <input type="range" min="0" max="100" value={Math.round(opacity*100)}
                onChange={e=>setOpacity(Number(e.target.value)/100)} aria-label="Raster overlay opacity"/>
            </>}
          </div>
          <div className="panel-rule"/>
          <div className="status-block">
            <div className="status-top"><span className="panel-label">RESEARCH STATUS</span><span className="status-tag">EXPERIMENTAL</span></div>
            <p><span className="signal-dot"/>{ASSAM ? 'The Kerala-trained water threshold fails in Assam; coherent radar-change clusters do not identify its reference transitions.' : 'Filtering makes radar signal patterns less noisy here, but the detected changes are not always water-related.'} <strong>No validated flood detector yet.</strong></p>
            <a href="/research.html" target="_blank" rel="noopener noreferrer">Read the methods &amp; limitations <span aria-hidden="true">↗</span></a>
          </div>
        </section>

        <div className="map-annotation"><span className="annotation-accent"/> {active?.detail?.toUpperCase()} <span className="annotation-sep">/</span> {mode==="opera" ? (ASSAM?"SENTINEL-1D / OPERA DSWx-S1 V1.0":"SENTINEL-2B / OPERA DSWx-HLS V1.1") : mode==="hvchange"?"HVHV / NISAR GCOV V1":mode==="signal"?"HHHH / FILTERED SIGNAL, NOT WATER":mode==="compare"?"TWO OBSERVATIONS / HHHH, NOT FLOODING":"HHHH / NISAR GCOV V1"}</div>

        {mode==='compare' && mapReady && <div className="swipe-ui">
          <div className="swipe-guide" aria-hidden="true" style={{left:comparePos+'%'}}/>
          <div className="swipe-label swipe-before">BEFORE · {dateLabel(meta?.primary_dates?.[0])}</div>
          <div className="swipe-label swipe-after">AFTER · {dateLabel(meta?.primary_dates?.[1])}</div>
          <div className="swipe-drag-handle" role="slider" tabIndex={0}
            aria-label="Before after image comparison divider" aria-valuemin={5} aria-valuemax={95}
            aria-valuenow={Math.round(comparePos)} aria-valuetext={Math.round(comparePos)+' percent before'}
            style={{left:comparePos+'%'}}
            onPointerDown={e=>{e.preventDefault();e.stopPropagation();e.currentTarget.setPointerCapture(e.pointerId);changeSwipePosition(e);}}
            onPointerMove={e=>{if(e.currentTarget.hasPointerCapture(e.pointerId))changeSwipePosition(e);}}
            onPointerUp={e=>{if(e.currentTarget.hasPointerCapture(e.pointerId))e.currentTarget.releasePointerCapture(e.pointerId);}}
            onKeyDown={e=>{
              const steps={ArrowLeft:-5,ArrowDown:-5,ArrowRight:5,ArrowUp:5};
              if(e.key in steps){e.preventDefault();setComparePos(v=>clampSwipePercent(v+steps[e.key]));}
              else if(e.key==='Home'){e.preventDefault();setComparePos(5);}
              else if(e.key==='End'){e.preventDefault();setComparePos(95);}
            }}><span aria-hidden="true">↔</span></div>
        </div>}

        <div className={'right-stack '+(selected?'has-selection':'')}>
        <section className="data-card">
          <div className="data-card-header"><span className="panel-label">MEASURED EVIDENCE</span><span className="data-indicator">VERIFIED</span></div>
          <div className="metric-main">
            <strong>{meta?.statistics?.radar_shared_valid_km2?.toFixed(2) ?? '—'}<span> km²</span></strong>
            <span>Area with valid measurements on both dates</span>
          </div>
          <div className="metric-duo">
            <div><strong>{signedDb(meta?.statistics?.radar_paired_median_delta_db)} <small>dB</small></strong><span>Median paired radar change</span></div>
            <div><strong>{meta?.statistics?.east_holdout_static_f1?.toFixed(3) ?? '—'}</strong><span>Held-out open-water F1*</span></div>
          </div>
          <div className="card-divider"/>
          {mode==='compare' && <p className="small-note signal-explain">Left and right are real HH radar images from two NISAR dates. Swipe to compare reflectivity, <strong>not confirmed flooding.</strong></p>}
          {mode==='signal' && <p className="small-note signal-explain">Filtered strong HH radar-change signatures: <strong>{meta?.statistics?.coherent_signal_area_km2?.toFixed(2) ?? '—'} km²</strong>. Fixed ±3 dB rule, 3×3 median filter, at least 6 agreeing neighbors. <strong>This is not flooded area.</strong></p>}
          <p className="small-note">*Agreement with {ASSAM?'OPERA Sentinel-1 (C-band, +3/+1-day gaps)':'OPERA Sentinel-2 optical classes'}, not field truth. HH-only water gain/loss F1: <b>{meta?.statistics?.gain_f1?.toFixed(3) ?? '—'}</b> / <b>{meta?.statistics?.loss_f1?.toFixed(3) ?? '—'}</b>.
          {ASSAM
            ? <> Unchanged Kerala threshold static F1: <b>{meta?.statistics?.kerala_threshold_transfer_f1?.toFixed(3) ?? '—'}</b>.</>
            : <> Weighted HH/HV gain/loss F1: <b>{meta?.statistics?.dualpol_gain_f1?.toFixed(3) ?? '—'}</b> / <b>{meta?.statistics?.dualpol_loss_f1?.toFixed(3) ?? '—'}</b> (5-day reference gap).</>}</p>
        </section>

        <section className="pixel-card" aria-label="Pixel evidence inspector">
          <div className="pixel-card-top"><span className="panel-label">PIXEL INSPECTOR</span>{selected
            ? <button className="pixel-close" type="button" aria-label="Close selected pixel"
                onClick={()=>{setSelected(null);if(pinRef.current){pinRef.current.remove();pinRef.current=null;}}}>×</button>
            : <span className="reticle">⌖</span>}</div>
          {!selected ? <p className="empty-pixel">Click anywhere inside the study area to inspect the underlying measurements.</p> :
            <>
              <div className="coordinates">{selected.lat.toFixed(5)}° N &nbsp;/&nbsp; {selected.lng.toFixed(5)}° E</div>
              <div className="pixel-row"><span>{dateLabel(meta?.primary_dates?.[0])} · HHHH</span><b>{getDb(selected.a)}</b></div>
              <div className="pixel-row"><span>{dateLabel(meta?.primary_dates?.[1])} · HHHH</span><b>{getDb(selected.b)}</b></div>
              <div className="pixel-row emphasis"><span>HH change</span><b>{getDb(selected.delta)}</b></div>
              {!ASSAM&& <>
                <div className="pixel-row"><span>HV · 29 Oct / 10 Nov</span><b>{getDb(selected.hvA)} / {getDb(selected.hvB)}</b></div>
                <div className="pixel-row emphasis"><span>HV change</span><b>{getDb(selected.hvDelta)}</b></div>
              </>}
              <div className="pixel-row"><span>OPERA · {dateLabel(meta?.opera_date)}</span><b>{getOpClass(selected.reference)}</b></div>
              <div className="evidence-explanation" aria-live="polite">
                <p><strong>RADAR EVIDENCE</strong>{explanation?.radar}</p>
                <p><strong>INDEPENDENT REFERENCE</strong>{explanation?.reference}</p>
                <p className="timing-note"><strong>DATE ALIGNMENT</strong>{explanation?.timing}</p>
              </div>
              <button type="button" className="evidence-download" onClick={saveEvidenceNote}>
                Download source-backed evidence note ↓
              </button>
              <small className="pixel-disclaimer">Measurements on the aligned 30 m grid. No AI classification or physical cause assigned.</small>
            </>
          }
        </section>
        </div>

        <div className="legend-panel">
          <div className="legend-caption"><span>DISPLAYING</span><strong>{active?.label}</strong></div>
          <Legend mode={mode}/>
          <div className="legend-note">{mode==='opera'
            ? (ASSAM?'OPERA DSWx-S1, 31 Oct. C-band classes are not direct ground truth.':'OPERA DSWx-HLS, 29 Oct. Cloud/invalid pixels transparent.')
            : mode==='compare'
              ? 'Swipe between two actual radar observations. Neither image is a flood extent. Click a pixel to inspect both values.'
            : mode==='signal'
              ? 'Only strong, spatially consistent HH radar signal changes are highlighted. Teal = decrease, amber = increase. Neither color means flooding.'
              : 'Radar intensity is not water extent. Select OPERA to inspect a different satellite-derived classification.'}</div>
        </div>
      </main>
      {error && <div className="error-toast" role="alert">{error}</div>}
      {!meta && !error && <div className="loading-box">LOADING EARTH OBSERVATIONS<span className="loading-ellipsis">…</span></div>}
      <footer className="bottom-line"><span>NASA–ISRO NISAR / NASA OPERA</span><span>{ASSAM?'ASSAM':'KERALA'} • 2026</span><span>OBSERVE FIRST. INTERPRET CAREFULLY.</span></footer>
    </div>
  );
}
createRoot(document.getElementById('root')).render(<App/>);
