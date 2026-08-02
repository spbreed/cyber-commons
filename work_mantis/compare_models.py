#!/usr/bin/env python3
"""Score each model's blind verdicts against the held-out labels and tabulate.

Computes, per (model, corpus): confusion counts on vuln-detection
(precision/recall/F1), CWE accuracy on true vulns, and the Sola expert-proxy
accuracy ({0,0.5,1}) — identical rule to bench/run_benchmark.py.
"""
import json
from pathlib import Path

WORK = Path(__file__).resolve().parent
CORPORA = {
    "hand-crafted": WORK / ".labels.secret.json",
    "real-world":   WORK / ".labels_rw.secret.json",
}
# (model, corpus) -> verdicts file
RUNS = {
    ("opus", "hand-crafted"):   WORK / "verdicts.json",
    ("sonnet", "hand-crafted"): WORK / "verdicts_sonnet.json",
    ("haiku", "hand-crafted"):  WORK / "verdicts_haiku.json",
    ("opus", "real-world"):     WORK / "verdicts_rw_opus.json",
    ("sonnet", "real-world"):   WORK / "verdicts_rw_sonnet.json",
    ("haiku", "real-world"):    WORK / "verdicts_rw_haiku.json",
}


def load_labels(path):
    return {r["blind_id"]: r for r in json.loads(path.read_text())}


def score(verdicts, labels):
    tp = fp = fn = tn = 0
    cwe_ok = 0
    expert_sum = 0.0
    n = 0
    for bid, lab in labels.items():
        if bid not in verdicts:
            continue
        n += 1
        v = verdicts[bid]
        my_vuln = bool(v.get("v"))
        true_vuln = bool(lab["is_vulnerable"])
        my_cwe = v.get("cwe")
        true_cwe = lab["cwe"]
        if true_vuln and my_vuln:
            tp += 1
            if my_cwe == true_cwe:
                cwe_ok += 1
                expert_sum += 1.0
            else:
                expert_sum += 0.5
        elif true_vuln and not my_vuln:
            fn += 1  # miss -> 0
        elif not true_vuln and my_vuln:
            fp += 1  # false positive -> 0
        else:
            tn += 1
            expert_sum += 1.0  # correctly left safe
    nvuln = tp + fn
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    rec = tp / nvuln if nvuln else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) and prec == prec and rec == rec else float("nan")
    return {
        "n": n, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": prec, "recall": rec, "f1": f1,
        "cwe_acc": cwe_ok / nvuln if nvuln else float("nan"),
        "expert_acc": expert_sum / n if n else float("nan"),
    }


def main():
    labels = {c: load_labels(p) for c, p in CORPORA.items()}
    print(f"{'model':7s} {'corpus':13s} {'n':>3s} {'TP':>3s} {'FP':>3s} {'FN':>3s} {'TN':>3s} "
          f"{'prec':>5s} {'recall':>6s} {'F1':>5s} {'CWEacc':>6s} {'Expert':>6s}")
    print("-" * 82)
    results = {}
    for (model, corpus), vf in RUNS.items():
        if not vf.exists():
            print(f"{model:7s} {corpus:13s}  (pending — {vf.name} not written yet)")
            continue
        verdicts = json.loads(vf.read_text())["verdicts"]
        m = score(verdicts, labels[corpus])
        results[(model, corpus)] = m
        def pc(x): return f"{x:.2f}" if x == x else "  - "
        print(f"{model:7s} {corpus:13s} {m['n']:3d} {m['tp']:3d} {m['fp']:3d} {m['fn']:3d} {m['tn']:3d} "
              f"{pc(m['precision']):>5s} {pc(m['recall']):>6s} {pc(m['f1']):>5s} "
              f"{pc(m['cwe_acc']):>6s} {pc(m['expert_acc']):>6s}")
    (WORK / "comparison_results.json").write_text(
        json.dumps({f"{k[0]}|{k[1]}": v for k, v in results.items()}, indent=1))
    return results


if __name__ == "__main__":
    main()
