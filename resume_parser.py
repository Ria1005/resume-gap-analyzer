"""
Resume parser (Phase 2 / M2): PDF + DOCX -> clean text -> sections -> skills -> JSON
Usage:   python resume_parser.py resume.pdf
         python resume_parser.py resume.docx
         python resume_parser.py folder_with_resumes/     (batch -> parsed_resumes.csv)
Needs:   pip install pdfplumber python-docx pandas
"""
import re, sys, json
from pathlib import Path
import pandas as pd

# ---------- 1. text extraction ----------
def read_pdf(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages)

def read_docx(path):
    import docx
    d = docx.Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:                                   # resumes often use tables for layout
        for row in t.rows:
            parts += [c.text for c in row.cells]
    return "\n".join(parts)

def read_file(path):
    ext = Path(path).suffix.lower()
    if ext == ".pdf":  return read_pdf(path)
    if ext == ".docx": return read_docx(path)
    if ext == ".txt":  return Path(path).read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"Unsupported file type: {ext}")

def clean_text(t):
    t = t.replace("\ufffd", " ").replace("\u2022", "\n- ").replace("\u2013", "-")
    t = re.sub(r"[^\x09\x0A\x20-\x7E]", " ", t)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()

# ---------- 2. section detection ----------
SECTIONS = {
    "summary":        r"summary|profile|objective|about me|career objective",
    "skills":         r"(technical |key |core )?skills?( set)?|technologies|tools|competenc(y|ies)",
    "experience":     r"(work |professional )?experience|employment|work history|internships?",
    "education":      r"education(al)?( details| qualifications?)?|academics?|qualifications?",
    "projects":       r"projects?|academic projects?",
    "certifications": r"certifications?|courses|licen[sc]es|training",
}
HEAD = {k: re.compile(rf"^\s*({v})\s*:?\s*$", re.I) for k, v in SECTIONS.items()}

def split_sections(text):
    out, cur = {"header": []}, "header"
    for line in text.split("\n"):
        s = line.strip()
        hit = next((k for k, p in HEAD.items() if s and len(s) < 40 and p.match(s)), None)
        if hit: cur = hit; out.setdefault(cur, []); continue
        out.setdefault(cur, []).append(line)
    return {k: "\n".join(v).strip() for k, v in out.items() if "\n".join(v).strip()}

# ---------- 3. contact + facts ----------
def contact(text):
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone = re.search(r"(\+?\d[\d\s\-()]{8,14}\d)", text)
    return {"email": email.group(0) if email else "", "phone": phone.group(0).strip() if phone else ""}

def years_experience(text):
    m = re.findall(r"(\d{1,2})\+?\s*(?:years?|yrs?)", text, re.I)
    return max(map(int, m)) if m else 0

# ---------- 4. skill extraction (taxonomy + synonyms) ----------
AMBIG = {"ts","tf","dl","ml","py","node","shell","torch","vue","mongo","team lead","collaboration","containers"}
def load_patterns(tax_path=None):
    tax_path = tax_path or Path(__file__).with_name("skills_taxonomy.csv")
    tax = pd.read_csv(tax_path).fillna("")
    pats = {}
    for _, r in tax.iterrows():
        if r.skill == "R": continue
        names = [r.skill] + [s for s in r.synonyms.split(";") if s and s not in AMBIG]
        pats[r.skill] = re.compile(r"(?<![a-z0-9+#.])(" + "|".join(re.escape(n.lower()) for n in names) + r")(?![a-z0-9+#])")
    return pats, dict(zip(tax.skill, tax.category))

def extract_skills(text, pats):
    low = text.lower()
    return [s for s, p in pats.items() if p.search(low)]

# ---------- 5. main parse ----------
_PATS = None
def parse_resume(path):
    global _PATS
    if _PATS is None: _PATS = load_patterns()
    pats, cats = _PATS
    text = clean_text(read_file(path))
    sec = split_sections(text)
    skills = extract_skills(text, pats)
    return {"file": Path(path).name, "chars": len(text), "sections_found": [k for k in sec if k != "header"],
            **contact(text), "years_experience": years_experience(text),
            "skills": skills, "skills_by_category": {c: [s for s in skills if cats[s] == c] for c in sorted({cats[s] for s in skills})},
            "sections": sec}

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    target = Path(sys.argv[1])
    if target.is_dir():
        rows = []
        for f in sorted(target.iterdir()):
            if f.suffix.lower() in (".pdf", ".docx", ".txt"):
                r = parse_resume(f); rows.append({**{k: r[k] for k in ("file","email","phone","years_experience","chars")},
                    "sections_found": ";".join(r["sections_found"]), "skills": ";".join(r["skills"])})
        pd.DataFrame(rows).to_csv("parsed_resumes.csv", index=False); print(f"Parsed {len(rows)} files -> parsed_resumes.csv")
    else:
        print(json.dumps(parse_resume(target), indent=2))
