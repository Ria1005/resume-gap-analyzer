"""
Home Page - Resume-to-Job Gap Analyzer.
Provides problem statement, project workflow, summary metrics, and entry point.
"""

import streamlit as st
import site_config
from ui_components import apply_theme, render_header, render_footer
from data_loader import load_dataset_summary

apply_theme()
render_header()

st.title(site_config.PROJECT)
st.markdown("<p style='font-size: 1.1rem; color: #4B515D; margin-top: -0.5rem; margin-bottom: 2rem;'>An automated skill coverage and gap detection tool for job seekers and recruiters.</p>", unsafe_allow_html=True)

# Problem statement in 3-4 plain sentences
st.subheader("The problem")
st.markdown(
    """
Job seekers often apply for positions without knowing how closely their resume matches what the employer wants.
Resumes get rejected by applicant tracking systems and recruiters simply because specific skills or keywords are missing.
Comparing a resume against a job description by hand is slow, subjective, and difficult to do consistently.
I built this project to automate that comparison so applicants can identify gaps and improve their resumes before submitting them.
    """
)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# How the project solves it
st.subheader("How it works")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="stat-box">
            <div class="step-num">1. Read the resume</div>
            <div class="step-desc">Extract text from PDF, Word (.docx) or text files, detect key sections, and extract technical and professional skills.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """
        <div class="stat-box">
            <div class="step-num">2. Read the job description</div>
            <div class="step-desc">Parse required and preferred skills from the posting text using a structured 73-skill taxonomy.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """
        <div class="stat-box">
            <div class="step-num">3. Compare and report</div>
            <div class="step-desc">Calculate weighted coverage, grant partial credit for related skills (like MySQL for SQL), and generate action items.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="info-note">
<strong>What you get:</strong> An overall match score (0 to 100), an exact breakdown of skills you have, partly matching skills, missing skills categorized by priority, and targeted advice on what projects or courses to complete next.
</div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# 4 Real numbers from results
summary, warnings = load_dataset_summary()
for w in warnings:
    st.caption(f"Note: {w}")

st.subheader("Key project metrics")
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
        <div class="stat-box">
            <div class="stat-num">{summary.get('num_skills', 73)}</div>
            <div class="stat-label">Skills defined in taxonomy across 9 domains</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
        <div class="stat-box">
            <div class="stat-num">{summary.get('num_pairs', 88)}</div>
            <div class="stat-label">Labelled resume-job pairs evaluated</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    f1_val = summary.get('skill_f1', 95.2)
    st.markdown(
        f"""
        <div class="stat-box">
            <div class="stat-num">{f1_val:.1f}%</div>
            <div class="stat-label">Skill extraction F1 score on resumes</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    acc_val = summary.get('fit_accuracy', 90.9)
    st.markdown(
        f"""
        <div class="stat-box">
            <div class="stat-num">{acc_val:.1f}%</div>
            <div class="stat-label">Fit label classification accuracy</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)

if st.button("Try the analyzer", type="primary"):
    st.switch_page("views/analyzer.py")

render_footer()
