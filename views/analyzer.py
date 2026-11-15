"""
Analyzer Page - Resume-to-Job Gap Analyzer.
Main working tool for uploading resumes, entering job descriptions, and evaluating skill fit.
"""

from pathlib import Path
import tempfile
import streamlit as st
from gap_engine import analyse_text, report, ADVICE, CATEGORY
from ui_components import (
    apply_theme,
    render_header,
    render_footer,
    render_tag_list,
)

apply_theme()
render_header()

st.title("Analyzer")
st.markdown("<p style='font-size: 1.05rem; color: #4B515D; margin-top: -0.5rem;'>Upload a candidate resume and paste a job posting to run the gap analysis engine.</p>", unsafe_allow_html=True)

# Sample loading actions
top_c1, top_c2 = st.columns([6, 2])
with top_c2:
    if st.button("Load sample", type="secondary"):
        st.session_state["use_sample"] = True
        sample_jd_path = Path("samples/jd_data_analyst.txt")
        if sample_jd_path.exists():
            st.session_state["jd_content"] = sample_jd_path.read_text(encoding="utf-8")
        st.session_state["auto_run"] = True
        st.rerun()

# Also support ?sample=true query parameter
if st.query_params.get("sample") == "true":
    st.session_state["use_sample"] = True
    sample_jd_path = Path("samples/jd_data_analyst.txt")
    if sample_jd_path.exists() and "jd_content" not in st.session_state:
        st.session_state["jd_content"] = sample_jd_path.read_text(encoding="utf-8")
        st.session_state["auto_run"] = True

using_sample = st.session_state.get("use_sample", False)

left, right = st.columns(2)

with left:
    st.subheader("1. Resume")
    uploaded_file = st.file_uploader(
        "Upload PDF, Word (.docx) or plain text (.txt)",
        type=["pdf", "docx", "txt"],
        key="resume_uploader"
    )
    if uploaded_file is not None:
        # If user uploads a file, turn off sample flag
        st.session_state["use_sample"] = False
        using_sample = False
        st.caption(f"Loaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
    elif using_sample:
        sample_resume_path = Path("samples/sample_resume_A.pdf")
        if sample_resume_path.exists():
            st.info("Sample loaded: samples/sample_resume_A.pdf (Data Analyst)")
        else:
            st.warning("Sample resume file not found in samples/")

with right:
    st.subheader("2. Job description")
    initial_jd = st.session_state.get("jd_content", "")
    jd_text = st.text_area(
        "Paste the job description here",
        value=initial_jd,
        height=220,
        placeholder="Required skills: Python, SQL...\nPreferred skills: Pandas, Docker...",
        key="jd_input_area"
    )
    st.caption("Tip: Use 'Required skills:' and 'Preferred skills:' headings for weighted scoring (70% / 30%).")

col_btn1, col_btn2 = st.columns([2, 6])
with col_btn1:
    analyse_clicked = st.button("Analyse", type="primary")
with col_btn2:
    if using_sample:
        if st.button("Clear sample", type="secondary"):
            st.session_state["use_sample"] = False
            st.session_state["jd_content"] = ""
            st.session_state["auto_run"] = False
            st.rerun()

# Run analysis when clicked or when auto_run is set
run_analysis = analyse_clicked or st.session_state.pop("auto_run", False)

if run_analysis:
    resume_file_to_parse = None
    temp_dir_obj = None

    if uploaded_file is not None:
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir_obj.name) / uploaded_file.name
        temp_path.write_bytes(uploaded_file.getvalue())
        resume_file_to_parse = temp_path
    elif using_sample:
        sample_path = Path("samples/sample_resume_A.pdf")
        if sample_path.exists():
            resume_file_to_parse = sample_path
        else:
            st.error("Sample file 'samples/sample_resume_A.pdf' was not found.")
            st.stop()
    else:
        st.warning("Please upload a resume or click 'Load sample'.")
        st.stop()

    if not jd_text.strip():
        st.warning("Please paste a job description.")
        st.stop()

    try:
        r = analyse_text(resume_file_to_parse, jd_text)
    except Exception as e:
        st.error(f"Could not read the resume: {e}")
        st.stop()
    finally:
        if temp_dir_obj is not None:
            temp_dir_obj.cleanup()

    if not r["req"] and not r["pref"]:
        st.error("No known skills were identified in the job description. Please provide a description that lists technical or soft skills from the taxonomy.")
        st.stop()

    # Results section
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.divider()

    # Big score and verdict
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; border: 1px solid #DCD8D0; border-radius: 4px; padding: 1.5rem 1.75rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #5F646E; font-weight: 600;">Match score</div>
                    <div style="font-family: Lora, Georgia, serif; font-size: 3rem; font-weight: 700; color: #1B365D; line-height: 1;">
                        {r['score']}%
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #5F646E; font-weight: 600;">Verdict</div>
                    <div style="font-family: Lora, Georgia, serif; font-size: 1.6rem; font-weight: 600; color: #142236;">
                        {r['verdict']} match
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #5F646E; font-weight: 600;">Required skills matched</div>
                    <div style="font-family: Lora, Georgia, serif; font-size: 1.6rem; font-weight: 600; color: #142236;">
                        {len(r['matched_req'])} / {len(r['req'])}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(min(int(r["score"]), 100))

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3 Column skill breakdown
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Skills you have**")
        have_skills = r["matched_req"] + r["matched_pref"]
        render_tag_list(have_skills, tag_type="have", fallback="No exact matches found")

    with col_b:
        st.markdown("**Partly matching**")
        partial_tags = [f"{s} (you have {o})" for s, o in (r["partial_req"] + r["partial_pref"])]
        render_tag_list(partial_tags, tag_type="partial", fallback="None")

    with col_c:
        st.markdown("**Missing skills**")
        missing_tags = [f"{s} (required)" for s in r["missing_req"]] + [f"{s} (preferred)" for s in r["missing_pref"]]
        render_tag_list(missing_tags, tag_type="missing", fallback="None")

    # Recommendations
    gaps = r["missing_req"] + r["missing_pref"] + [s for s, _ in r["partial_req"]]
    if gaps:
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.subheader("What to do")
        for s in r["missing_req"]:
            advice_text = ADVICE.get(CATEGORY.get(s, ""), "Add projects or relevant coursework demonstrating this skill.")
            st.markdown(f"&bull; **{s}** (required): {advice_text}")
        for s, o in r["partial_req"]:
            st.markdown(f"&bull; **{s}** (required): You know {o}. Mention it explicitly or spend a day learning {s}; both are in the same family.")
        for s in r["missing_pref"]:
            advice_text = ADVICE.get(CATEGORY.get(s, ""), "Add projects or relevant coursework demonstrating this skill.")
            st.markdown(f"&bull; **{s}** (preferred): {advice_text}")

    # Resume details
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    with st.expander("Details from resume"):
        st.markdown(f"**Identified skills:** {', '.join(r['resume_skills']) if r['resume_skills'] else 'None found'}")
        st.markdown(f"**Detected sections:** {', '.join(r['sections']) if r['sections'] else 'None detected'}")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    report_text = report(r)
    st.download_button(
        "Download report (.txt)",
        data=report_text,
        file_name="gap_report.txt",
        mime="text/plain"
    )

render_footer()
