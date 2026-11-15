"""
Validation (M5): test the gap engine on 88 labelled resume-job pairs.
Run:  python validate.py
Output: validation_report.txt  +  validation_results.csv
"""
import tempfile
from pathlib import Path
import numpy as np, pandas as pd
import gap_engine
from gap_engine import analyse_text
from resume_parser import parse_resume

# The labels were created WITHOUT the "SQL ~ MySQL" similarity rule, so switch it off for a fair test.
gap_engine.FAMILY["SQL"] = ""

res = pd.read_csv("data/resumes.csv").set_index("resume_id")
jds = pd.read_csv("data/job_descriptions.csv").set_index("jd_id")
pairs = pd.read_csv("data/pair_labels.csv").fillna("")
split = lambda s: set(x for x in s.split(";") if x)

tp = fp = fn = 0
rows = []
with tempfile.TemporaryDirectory() as d:
    # ---------- A. Skill extraction from resumes (precision / recall) ----------
    for rid, r in res.iterrows():
        (Path(d) / f"{rid}.txt").write_text(r.resume_text, encoding="utf-8")
        got = set(parse_resume(Path(d) / f"{rid}.txt")["skills"]) - {"R"}
        truth = split(r.skills) - {"R"}              # "R" is deliberately not supported (too ambiguous in text)
        tp += len(truth & got); fp += len(got - truth); fn += len(truth - got)
    prec, rec = tp / (tp + fp), tp / (tp + fn); f1 = 2 * prec * rec / (prec + rec)

    # ---------- B. Full gap analysis on every pair ----------
    for _, p in pairs.iterrows():
        out = analyse_text(Path(d) / f"{p.resume_id}.txt", jds.loc[p.jd_id, "jd_text"], p.jd_id)
        miss_true, miss_pred = split(p.missing_required), set(out["missing_req"])
        rows.append(dict(pair_id=p.pair_id, split=p.split, true_score=p.match_score, pred_score=out["score"],
                         true_fit=p.fit_label, pred_fit=out["verdict"],
                         miss_tp=len(miss_true & miss_pred), miss_fp=len(miss_pred - miss_true), miss_fn=len(miss_true - miss_pred)))
df = pd.DataFrame(rows); df["abs_error"] = (df.true_score - df.pred_score).abs()
df.to_csv("validation_results.csv", index=False)

def summary(x, name):
    mp = x.miss_tp.sum() / max(1, x.miss_tp.sum() + x.miss_fp.sum()); mr = x.miss_tp.sum() / max(1, x.miss_tp.sum() + x.miss_fn.sum())
    return [f"{name} ({len(x)} pairs)",
            f"  Fit label accuracy (Strong/Moderate/Weak): {100*(x.true_fit==x.pred_fit).mean():.1f}%",
            f"  Score: mean error {x.abs_error.mean():.1f} points, within 10 points: {100*(x.abs_error<=10).mean():.1f}%, correlation {np.corrcoef(x.true_score,x.pred_score)[0,1]:.3f}",
            f"  Missing-required-skill detection: precision {100*mp:.1f}%, recall {100*mr:.1f}%"]

conf = pd.crosstab(df.true_fit, df.pred_fit, rownames=["true"], colnames=["predicted"])
L = ["VALIDATION REPORT - Resume-to-Job Gap Analyzer", "=" * 60, "",
     f"A. Skill extraction from resumes ({len(res)} resumes)",
     f"  Precision {100*prec:.1f}%   Recall {100*rec:.1f}%   F1 {100*f1:.1f}%",
     "  (this is the 'agreement on identified skills'; target in the workplan: 80% or higher)", "",
     "B. Gap analysis vs ground-truth labels"] + summary(df, "All") + [""] + summary(df[df.split == "test"], "Test set only") + \
    ["", "Confusion matrix (all pairs):", conf.to_string(), "",
     "Note: ground truth is synthetic. See manual validation on real pairs for the real-world check."]
Path("validation_report.txt").write_text("\n".join(L), encoding="utf-8"); print("\n".join(L))
