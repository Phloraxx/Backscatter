#!/usr/bin/env python3
"""Backscatter: independent Cyclone Arnab NISAR / OPERA DSWx-S1 event case comparison.

Run *only after* the 2 NISAR HHHH Harmony GeoTIFFs and 2 OPERA S1 WTR TIFFs
have been downloaded with harmony_arnab.py and fetch_opera_arnab.py.

NISAR: 2026-10-22 and 2026-11-03; OPERA S1: 2026-10-23, 2026-11-04.
Reference is Sentinel-1 C-band radar classification, not field truth.
OPERA WTR classes: 0=not water, 1=open water, 3=inundated vegetation,
250=HAND masked, 251=layover/shadow, 254=ocean, 255=nodata.
Strict 0-vs-1 classification comparison excludes class 3 and all masks.

Only observed or truly computed results are reported. Never claim flooding
from this comparison. Dependencies: numpy, rasterio, optionally matplotlib.
"""
import json
from pathlib import Path

ROOT = Path.home() / "Downloads" / "backscatter-arnab-validated"
OUT = ROOT / "analysis"
DATES = ("2026-10-22", "2026-11-03")
REFERENCES = ("2026-10-23", "2026-11-04")
BBOX = (81.82,16.58,81.89,16.65)

def metrics(pred, actual, valid):
    import numpy as np
    tp=int((pred & actual & valid).sum())
    fp=int((pred & ~actual & valid).sum())
    fn=int((~pred & actual & valid).sum())
    tn=int((~pred & ~actual & valid).sum())
    denom=2*tp+fp+fn
    return dict(tp=tp,fp=fp,fn=fn,tn=tn,
                precision=round(tp/(tp+fp),4) if tp+fp else None,
                recall=round(tp/(tp+fn),4) if tp+fn else None,
                f1=round(2*tp/denom,4) if denom else None)

def load_reference(day):
    import numpy as np
    import rasterio
    candidates=list((ROOT/"opera_s1").glob(
        "OPERA_L3_DSWx-S1_T44QPD_"+day.replace("-","")+"*_B01_WTR.tif"))
    if len(candidates)!=1:
        raise FileNotFoundError("Expected exactly one downloaded OPERA DSWx-S1 WTR for "+day)
    return candidates[0]

def observe(radar_day, reference_day):
    import numpy as np
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.warp import transform_bounds,reproject,Resampling
    radar_path=ROOT/"nisar"/("nisar_"+radar_day+"_HHHH.tif")
    ref_path=load_reference(reference_day)
    if not radar_path.exists():
        raise FileNotFoundError("Missing authenticated NISAR subset: "+str(radar_path))
    with rasterio.open(radar_path) as radar, rasterio.open(ref_path) as ref:
        # Crop OPERA to actual NISAR subset geographic bounds.
        bounds=transform_bounds(radar.crs,ref.crs,*radar.bounds)
        window=from_bounds(*bounds,transform=ref.transform).round_offsets().round_lengths()
        classes=ref.read(1,window=window,boundless=True,fill_value=255)
        transform=ref.window_transform(window)
        raw=np.ma.asarray(radar.read(1,masked=True),dtype=np.float32).filled(np.nan)
        raw[~np.isfinite(raw)|(raw<=0)]=np.nan
        power=np.full(classes.shape,np.nan,dtype=np.float32)
        reproject(source=raw,destination=power,src_transform=radar.transform,
                  src_crs=radar.crs,src_nodata=np.nan,dst_transform=transform,
                  dst_crs=ref.crs,dst_nodata=np.nan,
                  resampling=Resampling.average,num_threads=1)
        with np.errstate(invalid="ignore",divide="ignore"):
            power=10*np.log10(power)
        power[~np.isfinite(power)]=np.nan
        vals,counts=np.unique(classes,return_counts=True)
        return dict(date=radar_day,ref_date=reference_day,radar_db=power,
            labels=classes,grid_transform=tuple(transform),grid_crs=str(ref.crs),
            reference_filename=ref_path.name,
            class_counts={str(int(v)):int(c) for v,c in zip(vals,counts)},
            pixel_area_km2=abs(transform.a*transform.e-transform.b*transform.d)/1e6)

def main():
    import numpy as np
    first=observe(DATES[0],REFERENCES[0])
    second=observe(DATES[1],REFERENCES[1])
    if first["radar_db"].shape!=second["radar_db"].shape or (
            first["grid_transform"]!=second["grid_transform"] or
            first["grid_crs"]!=second["grid_crs"]):
        raise RuntimeError("OPERA reference grids are not aligned")
    a,b=first["radar_db"],second["radar_db"]
    oa,ob=first["labels"],second["labels"]
    common=np.isfinite(a)&np.isfinite(b)
    strict_first=np.isin(oa,[0,1])&common
    strict_second=np.isin(ob,[0,1])&common
    strict_pair=strict_first&strict_second
    if int(strict_first.sum())<200:
        raise RuntimeError("Too few strict reference pixels for evaluation")

    west=np.indices(a.shape)[1]<a.shape[1]//2
    train=strict_first&west
    test=strict_first&~west
    if int(train.sum())<100 or int(test.sum())<100:
        raise RuntimeError("Train/test splits too small or masked")
    if int((train & (oa==1)).sum())<10 or int((train & (oa==0)).sum())<10:
        raise RuntimeError("Insufficient open-water/non-water examples in train split")
    best=None
    for th in np.arange(-28.,-2.,0.25):
        pred=a<=th
        current=metrics(pred,oa==1,train)
        if best is None or current["f1"]>best[1]["f1"]:
            best=(float(th),current)
    threshold=best[0]
    pa,pb=(a<=threshold),(b<=threshold)
    y0,y1=(oa==1),(ob==1)
    valid0,valid1=int(strict_first.sum()),int(strict_second.sum())
    with np.errstate(invalid="ignore"):
        delta=b-a
    vals=delta[common]

    # A genuine transfer test: apply Kerala's fitted HH-only cutoff unchanged.
    # The separately fitted Arnab cutoff is NOT an out-of-sample transfer experiment.
    kerala_threshold=-10.75
    transfer0=a<=kerala_threshold
    transfer1=b<=kerala_threshold
    transferred={
      "threshold_db":kerala_threshold,
      "first_reference_all_strict":metrics(transfer0,y0,strict_first),
      "second_reference_all_strict":metrics(transfer1,y1,strict_second),
      "candidate_gain_agreement":metrics(~transfer0&transfer1,~y0&y1,strict_pair),
      "candidate_loss_agreement":metrics(transfer0&~transfer1,y0&~y1,strict_pair),
      "caveat":"No Arnab threshold fitting; this is the unchanged Kerala cutoff measured against a different OPERA S1 reference."
    }
    medians={}
    for label in (0,1,3,250,251,254,255):
        medians[str(label)]={}
        for day,labels,radar in ((REFERENCES[0],oa,a),(REFERENCES[1],ob,b)):
            mask=(labels==label)&np.isfinite(radar)
            medians[str(label)][day]={
              "cells_with_radar":int(mask.sum()),
              "median_hhhh_db":round(float(np.median(radar[mask])),4) if mask.any() else None
            }
    transitions={}
    for left,right in ((0,0),(1,1),(3,3),(0,1),(1,0),(0,3),(3,0),(1,3),(3,1)):
        mask=(oa==left)&(ob==right)&common
        v=delta[mask]
        transitions[f"{left}_to_{right}"]={
          "cells":int(mask.sum()),
          "median_radar_delta_db":round(float(np.median(v)),4) if len(v) else None,
          "fraction_radar_decreased":round(float((v<0).mean()),4) if len(v) else None,
          "fraction_radar_increased":round(float((v>0).mean()),4) if len(v) else None
        }
    # Unchanged, zero-label SAR signal method previously evaluated in Kerala
    # and Assam. OPERA is used only for diagnostics AFTER masks are generated.
    from evaluate_signal_coherence import methods,render_signal
    radar_methods,_=methods(a,b)
    fixed_methods={}
    for method,(signal_down,signal_up) in radar_methods.items():
        stable_land=(oa==0)&(ob==0)&strict_pair
        flags=signal_down|signal_up
        fixed_methods[method]={
          "candidate_signal_area_km2":round(float(flags.sum()*first["pixel_area_km2"]),5),
          "candidate_cells":int(flags.sum()),
          "water_gain_vs_radar_decrease":metrics(signal_down,(oa==0)&(ob==1),strict_pair),
          "water_loss_vs_radar_increase":metrics(signal_up,(oa==1)&(ob==0),strict_pair),
          "stable_nonwater_signal_flag_fraction":round(
             float((flags&stable_land).sum() / (stable_land.sum() or 1)),5),
        }
    result={
       "study":"Cyclone Arnab temporal case: validated NISAR HHHH vs OPERA DSWx-S1",
       "sources":{
         "nisar_dates":list(DATES),"opera_s1_dates":list(REFERENCES),
         "opera_granules":[first["reference_filename"],second["reference_filename"]],
         "nisar_collection":"C3622241360-ASF",
         "opera_collection":"C2949811996-POCLOUD",
         "bbox_wgs84_lonlat":list(BBOX),
       },
       "reference_calendar_day_offsets":[1,1],
       "reference_hour_offsets":[11.2025,11.2022],
       "event_context":"IMD Cyclone Arnab landfall 28 Oct 2026 near 16.45N, 81.9E; this AOI is near that landfall, not field-verified flooded",
       "fixed_signal_methods_without_opera_training":fixed_methods,
       "reference_type":"Sentinel-1 C-band OPERA SAR water classification, NOT field ground truth",
       "evaluation_grid":str(first["grid_crs"]),
       "aoi_grid_shape":list(a.shape),
       "valid_radar_both_cells":int(common.sum()),
       "strict_class0_1_both_cells":int(strict_pair.sum()),
       "valid_reference_cells_first":valid0,
       "valid_reference_cells_second":valid1,
       "opera_class_counts":{REFERENCES[0]:first["class_counts"],REFERENCES[1]:second["class_counts"]},
       "median_nisar_delta_db":round(float(np.median(vals)),4) if len(vals) else None,
       "shared_valid_radar_area_km2":round(float(common.sum()*first["pixel_area_km2"]),5),
       "unmodified_kerala_threshold_transfer":transferred,
       "opera_class_radar_medians_db":medians,
       "opera_class_transitions_vs_nisar_delta":transitions,
       "fitted_water_threshold_db":threshold,
       "first_reference_west_train":best[1],
       "first_reference_east_test":metrics(pa,y0,test),
       "second_reference_transfer":metrics(pb,y1,strict_second),
       "candidate_gain_agreement":metrics(~pa&pb,~y0&y1,strict_pair),
       "candidate_loss_agreement":metrics(pa&~pb,y0&~y1,strict_pair),
       "reference_gain_cells":int((~y0&y1&strict_pair).sum()),
       "reference_loss_cells":int((y0&~y1&strict_pair).sum()),
       "inundated_vegetation_class3_cells":{REFERENCES[0]:int((oa==3).sum()),
            REFERENCES[1]:int((ob==3).sum())},
       "limitations":[
           "Both OPERA Sentinel-1D references are 1 calendar day after their NISAR acquisition.",
           "OPERA S1 is an independent C-band radar classification, not field-confirmed water extent.",
           "Class 3 inundated vegetation is excluded from strict 0-versus-1 evaluation.",
           "This water-change experiment uses only one region and a date-mismatched two-scene pair.",
           "ASF documents possible pre-Nov-12 calibration residuals in some radar modes; affected RCIDs have not been identified for these granules.",
           "No causal attribution, flood impacts, or field-validation accuracy is established."
       ]
    }
    OUT.mkdir(parents=True,exist_ok=True)
    render_signal(*radar_methods["coherent"],OUT/"arnab_coherent_signal.png")
    path=OUT/"arnab_nisar_opera_diagnostic.json"
    path.write_text(json.dumps(result,indent=2)+"\n")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig,axs=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
        for ax,arr,title,limits in zip(
            axs,(a,b,delta),
            ("NISAR HHHH Oct 22 (dB)","NISAR HHHH Nov 03 (dB)","HH change Nov 03 minus Oct 22 (dB)"),
            ((-27,0),(-27,0),(-8,8))):
            im=ax.imshow(np.ma.masked_invalid(arr),cmap="coolwarm" if "change" in title else "viridis",
                vmin=limits[0],vmax=limits[1])
            fig.colorbar(im,ax=ax,shrink=.75)
            ax.set_title(title);ax.axis("off")
        fig.suptitle("Cyclone Arnab study — measured NISAR backscatter, NOT confirmed flooding")
        fig.savefig(OUT/"arnab_radar_change.png",dpi=140)
        plt.close(fig)
    except ImportError:pass
    print("SAVED",path)
    for k in ("valid_radar_both_cells","strict_class0_1_both_cells","median_nisar_delta_db",
              "fitted_water_threshold_db","first_reference_east_test","second_reference_transfer",
              "candidate_gain_agreement","candidate_loss_agreement"):
        print(k,result[k])
    print("UNCHANGED_SIGNAL_METHODS",fixed_methods)
    print("KERALA_THRESHOLD_TRANSFER",transferred)
    print("CLASS_MEDIANS",medians)
    print("REFERENCE_CLASS_TRANSITIONS",transitions)

if __name__=="__main__":
    main()
