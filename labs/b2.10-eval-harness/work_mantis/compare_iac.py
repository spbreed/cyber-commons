#!/usr/bin/env python3
"""Score each model's IaC category findings against the Checkov-derived truth.

Multi-label: per (file, category) pair. Reports micro precision/recall/F1
(pooled over all pairs) and macro-F1 (mean over files), plus per-category recall.
"""
import json
from pathlib import Path

WORK = Path(__file__).resolve().parent
TRUTH = {r["blind_id"]: set(r["categories"]) for r in json.loads((WORK/".labels_iac.secret.json").read_text())}
RUNS = {
    "opus":   WORK/"iac_opus.json",
    "sonnet": WORK/"iac_sonnet.json",
    "haiku":  WORK/"iac_haiku.json",
}
CATS = ["SECRETS","VERSIONING","PUBLIC_ACCESS","NETWORK_CONTROLS","TRANSIT_TLS",
        "ENCRYPTION","LOGGING_MONITORING","BACKUP_DR","IAM_ACCESS","HARDENING"]


def score(findings):
    tp=fp=fn=0; f1s=[]
    per_cat_tp={c:0 for c in CATS}; per_cat_fn={c:0 for c in CATS}
    for bid, truth in TRUTH.items():
        pred = set(findings.get(bid, []))
        t_tp = len(pred & truth); t_fp = len(pred - truth); t_fn = len(truth - pred)
        tp+=t_tp; fp+=t_fp; fn+=t_fn
        p = t_tp/(t_tp+t_fp) if (t_tp+t_fp) else 1.0
        r = t_tp/(t_tp+t_fn) if (t_tp+t_fn) else 1.0
        f1s.append(2*p*r/(p+r) if (p+r) else 0.0)
        for c in truth:
            if c in pred: per_cat_tp[c]+=1
            else: per_cat_fn[c]+=1
    prec = tp/(tp+fp) if (tp+fp) else float("nan")
    rec = tp/(tp+fn) if (tp+fn) else float("nan")
    micro_f1 = 2*prec*rec/(prec+rec) if (prec+rec) else float("nan")
    return {"tp":tp,"fp":fp,"fn":fn,"precision":prec,"recall":rec,
            "micro_f1":micro_f1,"macro_f1":sum(f1s)/len(f1s),
            "per_cat_recall":{c:(per_cat_tp[c]/(per_cat_tp[c]+per_cat_fn[c]) if (per_cat_tp[c]+per_cat_fn[c]) else float("nan")) for c in CATS}}


def main():
    print(f"IaC (TerraGoat) multi-label detection vs Checkov — {len(TRUTH)} files\n")
    print(f"{'model':7s} {'TP':>3s} {'FP':>3s} {'FN':>3s} {'prec':>5s} {'recall':>6s} {'microF1':>7s} {'macroF1':>7s}")
    print("-"*52)
    results={}
    for model, vf in RUNS.items():
        if not vf.exists():
            print(f"{model:7s}  (pending — {vf.name})"); continue
        findings = json.loads(vf.read_text())["findings"]
        m = score(findings); results[model]=m
        print(f"{model:7s} {m['tp']:3d} {m['fp']:3d} {m['fn']:3d} "
              f"{m['precision']:.2f} {m['recall']:6.2f} {m['micro_f1']:7.2f} {m['macro_f1']:7.2f}")
    if results:
        print("\nper-category recall:")
        print(f"  {'category':20s} " + " ".join(f"{mm:>7s}" for mm in results))
        for c in CATS:
            print(f"  {c:20s} " + " ".join(f"{results[mm]['per_cat_recall'][c]:7.2f}" for mm in results))
    (WORK/"iac_results.json").write_text(json.dumps(results,indent=1))


if __name__ == "__main__":
    main()
