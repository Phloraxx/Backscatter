#!/usr/bin/env python3
"""Evaluate a conservative NISAR HHHH -> OPERA DSWx-HLS diagnostic baseline.

Reproduce from locally downloaded NASA products:
 python scripts/compare_nisar_opera_hls.py   # optional diagnostic and plots
 python scripts/evaluate_change_baseline.py

- OPERA 0=nonwater, 1=open water; discard partial-water class 2 for strict evaluation.
- Train a simple backscatter threshold on the WEST half of Oct 29 scene only.
- Evaluate static-water agreement on EAST held-out half.
- Transfer threshold to the Nov 10 radar; compare with Nov 05 optical, with a
  documented 5-day mismatch. Assess candidate gained/lost-water masks honestly.
- Every reported metric is agreement with OPERA, NOT ground-truth flood accuracy.
"""
import json
from pathlib import Path
import numpy as np
import rasterio
from compare_nisar_opera_hls import ROOT, OUTPUT, read_pair

def confusion(pred, ref, valid):
    tp = int((pred & ref & valid).sum())
    fp = int((pred & ~ref & valid).sum())
    fn = int((~pred & ref & valid).sum())
    tn = int((~pred & ~ref & valid).sum())
    return {
        "TP":tp, "FP":fp, "FN":fn, "TN":tn,
        "precision":round(tp/(tp+fp),4) if tp+fp else 0.,
        "recall":round(tp/(tp+fn),4) if tp+fn else 0.,
        "f1":round(2*tp/(2*tp+fp+fn),4) if 2*tp+fp+fn else 0.,
        "iou":round(tp/(tp+fp+fn),4) if tp+fp+fn else 0.,
    }

def transition_metrics(a,b,valid_radar):
    radar_delta=b["radar_db"]-a["radar_db"]
    opt_a,opt_b=a["label"],b["label"]
    all_valid=np.isin(opt_a,[0,1,2])&np.isin(opt_b,[0,1,2])&valid_radar
    categories={
        "stable_nonwater": (opt_a==0)&(opt_b==0),
        "stable_openwater": (opt_a==1)&(opt_b==1),
        "new_openwater": (opt_a==0)&(opt_b==1),
        "lost_openwater": (opt_a==1)&(opt_b==0),
        "new_any_optical_water": (opt_a==0)&np.isin(opt_b,[1,2]),
        "lost_any_optical_water": np.isin(opt_a,[1,2])&(opt_b==0),
    }
    report={}
    for name, group in categories.items():
        mask=group & all_valid
        vals=radar_delta[mask]
        if not len(vals):
            report[name]={"cells":0};continue
        report[name]={
            "cells":int(mask.sum()),"area_km2":round(float(mask.sum())*.0009,4),
            "median_nisar_change_db":round(float(np.median(vals)),4),
            "fraction_radar_decreased":round(float((vals<0).mean()),4),
            "fraction_radar_increased":round(float((vals>0).mean()),4),
            "p10_p90_db":[round(float(v),4) for v in np.percentile(vals,[10,90])]
        }
    return report

def draw_map(a,b,cutoff,report):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    strict=np.isin(a["label"],[0,1])&np.isin(b["label"],[0,1])
    valid_radar=np.isfinite(a["radar_db"])&np.isfinite(b["radar_db"])
    a_ref=a["label"]==1;b_ref=b["label"]==1
    a_pred=a["radar_db"]<=cutoff;b_pred=b["radar_db"]<=cutoff
    def classes(w0,w1,valid):
        out=np.full(w0.shape,4,dtype=np.uint8)
        out[valid & ~w0 & ~w1]=0
        out[valid & w0 & w1]=1
        out[valid & ~w0 & w1]=2
        out[valid & w0 & ~w1]=3
        return out
    opt=classes(a_ref,b_ref,strict&valid_radar)
    pred=classes(a_pred,b_pred,valid_radar)
    cmap=ListedColormap(["#f7f7f7","#23669b","#29bd8a","#ec8f45","#999999"])
    fig,ax=plt.subplots(1,3,figsize=(13,4.8),constrained_layout=True)
    ax[0].imshow(opt,cmap=cmap,vmin=0,vmax=4,interpolation="nearest")
    ax[0].set_title("OPERA Oct 29 → Nov 05\nstrict 0/1 classes, clear pixels")
    ax[1].imshow(pred,cmap=cmap,vmin=0,vmax=4,interpolation="nearest")
    ax[1].set_title("NISAR Oct 29 → Nov 10\nsingle threshold "+str(cutoff)+" dB")
    delta=b["radar_db"]-a["radar_db"]
    im=ax[2].imshow(np.ma.masked_invalid(delta),vmin=-8,vmax=8,cmap="coolwarm")
    ax[2].set_title("NISAR HHHH radar change (dB)\nNov 10 minus Oct 29")
    fig.colorbar(im,ax=ax[2],shrink=.72,label="dB")
    for z in ax:z.axis("off")
    from matplotlib.patches import Patch
    patches=[Patch(facecolor=c,label=label) for c,label in [
        ("#f7f7f7","Nonwater both"),("#23669b","Water both"),
        ("#29bd8a","New water"),("#ec8f45","Water lost"),("#999999","Excluded")]]
    fig.legend(handles=patches,loc="lower center",ncol=5,bbox_to_anchor=(.4,-.01),fontsize=9)
    fig.suptitle("Kuttanad — change comparison is NOT same-date validation; second reference 5 days earlier",fontsize=11)
    output=OUTPUT/"change_baseline_comparison.png"
    fig.savefig(output,dpi=140,bbox_inches="tight")
    plt.close(fig)
    print("FIGURE",output)

def main():
    with rasterio.open(ROOT/"nisar_2026-10-29_hhhh_raw.tif") as src:
        bounds,crs=src.bounds,src.crs
    a=read_pair("2026-10-29","S2B","2026-10-29",bounds,crs)
    b=read_pair("2026-11-05","S2A","2026-11-10",bounds,crs)
    if a["label"].shape!=b["label"].shape or a["transform"]!=b["transform"]:
        raise RuntimeError("Reference rasters have incompatible geospatial grids")
    h,w=a["label"].shape
    rows,cols=np.indices((h,w))
    strictly_valid=(np.isin(a["label"],[0,1]) & np.isfinite(a["radar_db"]))
    training=strictly_valid & (cols<w//2)
    testing=strictly_valid & (cols>=w//2)
    y=a["label"]==1

    best=None
    for threshold in np.arange(-25.,-8.,0.25):
        pred=a["radar_db"]<=threshold
        values=confusion(pred,y,training)
        if best is None or values["f1"]>best["f1"]:
            best={"threshold_db":float(threshold),**values}
    cutoff=best["threshold_db"]

    east=confusion(a["radar_db"]<=cutoff,y,testing)
    near_date_valid=np.isin(b["label"],[0,1])&np.isfinite(b["radar_db"])
    near_date=confusion(b["radar_db"]<=cutoff,b["label"]==1,near_date_valid)
    both_valid=(np.isin(a["label"],[0,1]) & np.isin(b["label"],[0,1])
                & np.isfinite(a["radar_db"]) & np.isfinite(b["radar_db"]))
    nisar0=a["radar_db"]<=cutoff; nisar1=b["radar_db"]<=cutoff
    opt0=a["label"]==1;opt1=b["label"]==1
    gain=confusion(~nisar0&nisar1,~opt0&opt1,both_valid)
    loss=confusion(nisar0&~nisar1,opt0&~opt1,both_valid)
    directional=transition_metrics(a,b,np.isfinite(a["radar_db"])&np.isfinite(b["radar_db"]))
    report={
        "title":"Kuttanad static-water and candidate-change diagnostic",
        "nisar_dates":["2026-10-29","2026-11-10"],
        "opera_dates":["2026-10-29","2026-11-05"],
        "optical_reference_date_mismatch_second_days":5,
        "grid_m":30,
        "threshold_trained_on":"Oct 29 west-half cells, OPERA classes 0 vs 1 (partial class 2 excluded)",
        "threshold_train_west":best,
        "static_water_test_east":east,
        "static_water_test_east_pixels":int(testing.sum()),
        "static_water_transfer_nov05_optical_vs_nov10_radar":near_date,
        "candidate_gain_vs_opera_5day_offset":gain,
        "candidate_loss_vs_opera_5day_offset":loss,
        "change_evaluation_cells":int(both_valid.sum()),
        "reference_transition_nisar_sign_test":directional,
        "interpretation":[
            "A good static water-vs-land classifier does not imply reliable change mapping.",
            "New/lost open-water class transitions show directional radar changes, but gain/loss mask precision remains poor.",
            "OPERA is satellite-derived, not independent field ground truth.",
            "The second OPTICAL observation was Nov 05 while the second NISAR date was Nov 10.",
            "Threshold was supervised against OPERA on Oct 29 west half; east half is a geographically disjoint internal check.",
            "This script does not validate NISAR flood extent or disaster impacts."
        ],
    }
    OUTPUT.mkdir(parents=True,exist_ok=True)
    target=OUTPUT/"change_baseline.json"
    target.write_text(json.dumps(report,indent=2)+"\n")
    draw_map(a,b,cutoff,report)
    print("TRAIN_THRESHOLD",cutoff,"TRAIN_F1",best["f1"])
    print("STATIC_EAST_HOLDOUT",east,"N_TEST",int(testing.sum()))
    print("TRANSFER_NOV10_VS_NOV05",near_date)
    print("CHANGE_GAIN",gain)
    print("CHANGE_LOSS",loss)
    print("DIRECTIONAL",json.dumps({k:{"n":v.get("cells"),"median_db":v.get("median_nisar_change_db"),"decreased":v.get("fraction_radar_decreased"),"increased":v.get("fraction_radar_increased")} for k,v in directional.items()}))
    print("REPORT",target)

if __name__=="__main__":
    main()
