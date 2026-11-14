import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import * as maplibregl from 'maplibre-gl';
import proj4 from 'proj4';
import 'maplibre-gl/dist/maplibre-gl.css';
import './styles.css';

proj4.defs('EPSG:32643', '+proj=utm +zone=43 +datum=WGS84 +units=m +no_defs');

const LAYERS = [
  { id: 'oct29', label: '29 OCT', detail: 'NISAR · before', file: 'oct29.png' },
  { id: 'nov10', label: '10 NOV', detail: 'NISAR · after', file: 'nov10.png' },
  { id: 'change', label: 'RADAR CHANGE', detail: 'HH · 10 Nov − 29 Oct', file: 'change.png' },
  { id: 'hvchange', label: 'HV CHANGE', detail: 'HV · 10 Nov − 29 Oct', file: 'hv_change.png' },
  { id: 'opera', label: 'OPERA WATER', detail: 'Optical · 29 Oct', file: 'opera_oct29.png' },
];

const getDb = (v) => Number.isFinite(v) ? v.toFixed(2) + ' dB' : 'No valid reading';
const getOpClass = (v) => ({0:'Non-water',1:'Open water',2:'Partial water',252:'Masked / ice or sediment',253:'Cloud / cloud shadow',254:'Ocean mask',255:'No data'}[v] ?? 'Other / masked');

function Legend({mode}) {
  if (mode === 'opera') return (
    <div className="legend-row"><span><i className="dot water"/>Open water</span><span><i className="dot partial"/>Partial water</span><span><i className="dot land"/>Non-water</span><span><i className="dot invalid"/>Excluded</span></div>
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
  const [selected,setSelected] = useState(null);
  const [mapReady,setMapReady] = useState(false);
  const mapRef = useRef(null);
  const pinRef = useRef(null);
  const mapNode = useRef(null);

  useEffect(() => {
    let active = true;
    Promise.all([
      fetch('/data/meta.json').then(r=>{if(!r.ok)throw new Error('Missing dataset metadata');return r.json();}),
      fetch('/data/pixels.bin').then(r=>{if(!r.ok)throw new Error('Missing measurement data');return r.arrayBuffer();}),
    ]).then(([m,b]) => {if(active){setMeta(m);setBuffer(b);}}).catch(e=>{if(active)setError(e.message);});
    return ()=>{active=false};
  }, []);

  useEffect(() => {
    if(!meta || !buffer || !mapNode.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapNode.current,
      center: [76.455,9.435],
      zoom: 12.7,
      pitch: 0,
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
    const before = new Float32Array(buffer,0,len);
    const after = new Float32Array(buffer,4*len,len);
    const hvBefore = new Float32Array(buffer,8*len,len);
    const hvAfter = new Float32Array(buffer,12*len,len);
    const optical = new Uint8Array(buffer,16*len,len);
    const lngs=meta.image_coordinates_lonlat.map(x=>x[0]);
    const lats=meta.image_coordinates_lonlat.map(x=>x[1]);
    map.on('load', () => {
      for(const layer of LAYERS){
        map.addSource('image-'+layer.id,{type:'image',url:'/data/'+layer.file,
          coordinates:meta.image_coordinates_lonlat});
        map.addLayer({id:'layer-'+layer.id,source:'image-'+layer.id,type:'raster',
          layout:{visibility:layer.id==='change'?'visible':'none'},
          paint:{'raster-opacity':opacity,'raster-resampling':'nearest'}});
      }
      map.fitBounds([[Math.min(...lngs),Math.min(...lats)],[Math.max(...lngs),Math.max(...lats)]],
        {padding:{top:100,bottom:95,left:65,right:65},duration:0,maxZoom:15});
      setMapReady(true);
    });
    map.on('click',(e) => {
      const [x,y]=proj4('EPSG:4326','EPSG:32643',[e.lngLat.lng,e.lngLat.lat]);
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
    for(const layer of LAYERS){
      if(map.getLayer('layer-'+layer.id)){
        map.setLayoutProperty('layer-'+layer.id,'visibility',mode===layer.id?'visible':'none');
        map.setPaintProperty('layer-'+layer.id,'raster-opacity',opacity);
      }
    }
  },[mode,opacity,mapReady]);

  const active=LAYERS.find(l=>l.id===mode);
  return (
    <div className="shell">
      <div className="map-canvas" ref={mapNode} role="region" aria-label="Interactive NISAR radar image map of Kuttanad, Kerala"/>
      <div className="map-grain" aria-hidden="true"/>
      <header className="top-bar">
        <div className="brand-mark" aria-hidden="true"><span className="brand-orbit"/><span className="brand-cross"/></div>
        <div className="identity">
          <div className="wordmark">BACKSCATTER<span className="tiny-star">✳</span></div>
          <div className="subheading">RADAR EVIDENCE FOR A CHANGING EARTH</div>
        </div>
        <div className="mission">
          <span className="live-dot"/>NASA SPACE APPS 2026 <span className="mission-sep">/</span> AFTERIMAGE
        </div>
      </header>

      <main className="workspace">
        <section className="control-panel">
          <div className="overline"><span className="overline-line"/> FIELD STUDY 01 <span className="overline-faint">/ KERALA, INDIA</span></div>
          <h1>Kuttanad <em>through radar.</em></h1>
          <p className="intro">See what NASA–ISRO NISAR measured between two observations. Explore changing radar signals without confusing them with confirmed flood extents.</p>
          <div className="scene-meta"><span>09.43° N, 76.45° E</span><span className="bullet">·</span><span>10 m source data</span></div>
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
            <div className="opacity-caption"><span>OVERLAY OPACITY</span><output>{Math.round(opacity*100)}%</output></div>
            <input type="range" min="0" max="100" value={Math.round(opacity*100)}
              onChange={e=>setOpacity(Number(e.target.value)/100)} aria-label="Raster overlay opacity"/>
          </div>
          <div className="panel-rule"/>
          <div className="status-block">
            <div className="status-top"><span className="panel-label">RESEARCH STATUS</span><span className="status-tag">EXPERIMENTAL</span></div>
            <p><span className="signal-dot"/>HH + HV improves static-water agreement but worsens change-mask results. <strong>No validated flood detector yet.</strong></p>
            <a href="https://github.com/Phloraxx/Backscatter/blob/main/research/kuttanad_validated_2026_10_11/DUAL_POLARIZATION.md"
              target="_blank" rel="noreferrer">Read the methods &amp; limitations <span aria-hidden="true">↗</span></a>
          </div>
        </section>

        <div className="map-annotation"><span className="annotation-accent"/> {active?.detail?.toUpperCase()} <span className="annotation-sep">/</span> {mode === "opera" ? "SENTINEL-2B / OPERA DSWx-HLS V1.1" : mode === "hvchange" ? "HVHV / NISAR GCOV V1" : "HHHH / NISAR GCOV V1"}</div>

        <section className="data-card">
          <div className="data-card-header"><span className="panel-label">MEASURED EVIDENCE</span><span className="data-indicator">VERIFIED</span></div>
          <div className="metric-main">
            <strong>{meta?.statistics?.radar_shared_valid_km2?.toFixed(2) ?? '—'}<span> km²</span></strong>
            <span>Area with valid measurements on both dates</span>
          </div>
          <div className="metric-duo">
            <div><strong>+{meta?.statistics?.radar_paired_median_delta_db?.toFixed(2) ?? '—'} <small>dB</small></strong><span>Median paired radar change</span></div>
            <div><strong>{meta?.statistics?.same_day_opera_auc?.toFixed(3) ?? '—'}</strong><span>Oct 29 water/land ROC-AUC*</span></div>
          </div>
          <div className="card-divider"/>
          <p className="small-note">*OPERA product agreement, not field ground truth. HH-only change F1 gain/loss: <b>{meta?.statistics?.gain_f1?.toFixed(3) ?? '—'}</b> / <b>{meta?.statistics?.loss_f1?.toFixed(3) ?? '—'}</b>. Dual-pol F1: <b>{meta?.statistics?.dualpol_gain_f1?.toFixed(3) ?? '—'}</b> / <b>{meta?.statistics?.dualpol_loss_f1?.toFixed(3) ?? '—'}</b> (five-day reference gap).</p>
        </section>

        <section className="pixel-card">
          <div className="pixel-card-top"><span className="panel-label">PIXEL INSPECTOR</span><span className="reticle">⌖</span></div>
          {!selected ? <p className="empty-pixel">Click anywhere inside the study area to inspect the underlying measurements.</p> :
            <>
              <div className="coordinates">{selected.lat.toFixed(5)}° N &nbsp;/&nbsp; {selected.lng.toFixed(5)}° E</div>
              <div className="pixel-row"><span>29 Oct · HHHH</span><b>{getDb(selected.a)}</b></div>
              <div className="pixel-row"><span>10 Nov · HHHH</span><b>{getDb(selected.b)}</b></div>
              <div className="pixel-row emphasis"><span>HH change</span><b>{getDb(selected.delta)}</b></div>
              <div className="pixel-row"><span>HV · 29 Oct / 10 Nov</span><b>{getDb(selected.hvA)} / {getDb(selected.hvB)}</b></div>
              <div className="pixel-row emphasis"><span>HV change</span><b>{getDb(selected.hvDelta)}</b></div>
              <div className="pixel-row"><span>OPERA · 29 Oct</span><b>{getOpClass(selected.reference)}</b></div>
              <small className="pixel-disclaimer">Values sampled on the 30 m reference grid. No physical cause is assigned.</small>
            </>
          }
        </section>

        <div className="legend-panel">
          <div className="legend-caption"><span>DISPLAYING</span><strong>{active?.label}</strong></div>
          <Legend mode={mode}/>
          <div className="legend-note">{mode==='opera'?'OPERA DSWx-HLS, 29 Oct 2026. Cloud/invalid cells transparent.':'Radar intensity is not water extent. Select OPERA to inspect a separate satellite-derived classification.'}</div>
        </div>
      </main>
      {error && <div className="error-toast" role="alert">{error}</div>}
      {!meta && !error && <div className="loading-box">LOADING EARTH OBSERVATIONS<span className="loading-ellipsis">…</span></div>}
      <footer className="bottom-line"><span>NASA–ISRO NISAR / NASA OPERA</span><span>KERALA • 2026</span><span>OBSERVE FIRST. INTERPRET CAREFULLY.</span></footer>
    </div>
  );
}
createRoot(document.getElementById('root')).render(<App/>);
