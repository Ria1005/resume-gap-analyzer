"""
Gap engine (M3): compare ONE resume with ONE job description.
Usage:  python gap_engine.py samples/sample_resume_A.pdf samples/jd_data_analyst.txt
Output: match score, matched / partial / missing skills, recommendations -> printed + gap_report.txt
"""
import re, sys
from pathlib import Path
import pandas as pd
from resume_parser import parse_resume, extract_skills, load_patterns

TAX = pd.read_csv(Path(__file__).with_name("skills_taxonomy.csv")).fillna("")
FAMILY = dict(zip(TAX.skill, TAX.family))
CATEGORY = dict(zip(TAX.skill, TAX.category))
FAMILY["SQL"] = "sql_db"          # SQL is related to MySQL / PostgreSQL / SQLite
PATS, _ = load_patterns()

# what to suggest for each missing skill type
ADVICE = {
    "Programming": "Learn the basics and build one small project, then list it under Projects.",
    "Database":    "Practise with a free sample database and add a project that uses it.",
    "Data":        "Do a short course or tutorial, then add a dashboard or analysis you made.",
    "ML":          "Complete a beginner course and add one model you trained to Projects.",
    "Web":         "Build a small web app using it and put the link on your resume.",
    "DevOps":      "Follow a hands-on tutorial and add the tool to your Skills section.",
    "QA":          "Learn it through a short course and add a testing project.",
    "Business":    "Mention where you used it at work or college, or take a short course.",
    "Soft":        "Show it with an example in your Experience section.",
}

def read_jd(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")

def split_jd(text):
    """Skills before 'Preferred / Nice to have' = required; after it = preferred."""
    m = re.search(r"preferred|nice[\s-]to[\s-]have|good[\s-]to[\s-]have|desirable|bonus", text, re.I)
    if not m:
        return extract_skills(text, PATS), []
    req = extract_skills(text[:m.start()], PATS)
    pref = [s for s in extract_skills(text[m.start():], PATS) if s not in req]
    return req, pref

def classify(jd_skills, resume_skills):
    have = set(resume_skills); matched, partial, missing = [], [], []
    for s in jd_skills:
        if s in have: matched.append(s)
        else:
            sub = [o for o in have if FAMILY.get(s) and FAMILY.get(o) == FAMILY[s]]
            if sub: partial.append((s, sub[0]))
            else:   missing.append(s)
    return matched, partial, missing

def analyse(resume_path, jd_path):
    return analyse_text(resume_path, read_jd(jd_path), Path(jd_path).name)

def analyse_text(resume_path, jd_text, jd_name="pasted job description"):
    resume = parse_resume(resume_path)
    req, pref = split_jd(jd_text)
    rm, rp, rx = classify(req, resume["skills"])
    pm, pp, px = classify(pref, resume["skills"])
    req_cov = (len(rm) + 0.5 * len(rp)) / len(req) if req else 0
    if pref:
        pref_cov = (len(pm) + 0.5 * len(pp)) / len(pref)
        score = 100 * (0.7 * req_cov + 0.3 * pref_cov)
    else:
        score = 100 * req_cov
    verdict = "Strong" if score >= 75 else "Moderate" if score >= 50 else "Weak"
    return dict(resume=resume["file"], jd=jd_name, resume_skills=resume["skills"], sections=resume["sections_found"], score=round(score, 1), verdict=verdict,
                req=req, pref=pref, matched_req=rm, partial_req=rp, missing_req=rx,
                matched_pref=pm, partial_pref=pp, missing_pref=px)

def report(r):
    L = [f"RESUME: {r['resume']}   JOB: {r['jd']}", "=" * 60,
         f"MATCH SCORE: {r['score']}%   ({r['verdict']} match)", "",
         f"You have ({len(r['matched_req'])}/{len(r['req'])} required): " + (", ".join(r["matched_req"]) or "none")]
    if r["partial_req"]:
        L.append("Partly match: " + ", ".join(f"{s} (you have {o})" for s, o in r["partial_req"]))
    L.append("MISSING required: " + (", ".join(r["missing_req"]) or "none"))
    if r["pref"]:
        L += ["", f"Preferred skills you have: " + (", ".join(r["matched_pref"]) or "none"),
              "MISSING preferred: " + (", ".join(r["missing_pref"]) or "none")]
    gaps = r["missing_req"] + [s for s, _ in r["partial_req"]] + r["missing_pref"]
    if gaps:
        L += ["", "WHAT TO DO:"]
        for s in r["missing_req"]:  L.append(f" - {s} (required): {ADVICE[CATEGORY[s]]}")
        for s, o in r["partial_req"]: L.append(f" - {s} (required): you know {o}, so mention it or learn {s}; they are similar.")
        for s in r["missing_pref"]: L.append(f" - {s} (preferred): {ADVICE[CATEGORY[s]]}")
    return "\n".join(L)

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    r = analyse(sys.argv[1], sys.argv[2])
    txt = report(r); print(txt)
    Path("gap_report.txt").write_text(txt, encoding="utf-8")
    print("\n(saved to gap_report.txt)")
