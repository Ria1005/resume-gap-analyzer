"""
How to Use - Resume-to-Job Gap Analyzer.
Explains step-by-step instructions, input formatting tips, and scoring criteria.
"""

import streamlit as st
from ui_components import apply_theme, render_header, render_footer

apply_theme()
render_header()

st.title("How to use")
st.markdown("<p style='font-size: 1.05rem; color: #4B515D; margin-top: -0.5rem;'>Follow these steps to evaluate a resume against any job description.</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Step by step
st.subheader("Step-by-step guide")

steps = [
    ("1. Upload a resume", "Choose a file in PDF, Word (.docx), or plain text (.txt) format. Text-based files work best. The parser extracts your contact info, detected sections, and skills automatically."),
    ("2. Paste the job description", "Copy the complete job posting into the text area. You can include role summaries, requirements, and preferred qualifications."),
    ("3. Click Analyse", "The gap engine scans both documents, matches extracted skills against the 73-item taxonomy, and checks related skill families."),
    ("4. Read the report", "Review your overall match score, the verdict (Strong, Moderate, or Weak), the list of matched skills, partial matches, and missing skills."),
    ("5. Download the report", "Click the Download button to save the full text report for future reference, resume rewriting, or interview prep.")
]

for title, desc in steps:
    st.markdown(
        f"""
        <div class="step-item">
            <div class="step-num">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Tips box
st.subheader("Practical tips")
st.markdown(
    """
    <div class="info-note">
        <div style="margin-bottom: 0.5rem;"><strong>Heading conventions:</strong> If you separate the posting with headings like <em>Required skills</em> and <em>Preferred skills</em> (or <em>Nice to have</em>), the engine weights required skills at 70% and preferred skills at 30%. Without headings, all skills count equally.</div>
        <div><strong>Document format:</strong> Please upload a digital, text-based PDF or Word file rather than a scanned image. The parser reads the text stream directly and does not perform OCR.</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# Score explanation table
st.subheader("How the score is calculated")
st.markdown(
    """
The analyzer compares the skills listed in your resume against the skills extracted from the job description.
A skill can match in three ways:
1. <strong>Direct match:</strong> The exact skill or an accepted synonym appears in both documents (counts as 1.0 point).
2. <strong>Partial match:</strong> The resume lacks the exact skill but contains a closely related tool from the same family (e.g., MySQL when SQL is requested, or PostgreSQL when MySQL is requested). This counts as <strong>half credit (0.5 points)</strong>.
3. <strong>Missing:</strong> Neither the skill nor any family substitute is found (counts as 0 points).
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <table class="plain-table">
        <thead>
            <tr>
                <th style="width: 25%;">Score range</th>
                <th style="width: 20%;">Fit verdict</th>
                <th>Meaning</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>75% and above</strong></td>
                <td>Strong</td>
                <td>Candidate covers nearly all core requirements. Ready to apply with minimal adjustments.</td>
            </tr>
            <tr>
                <td><strong>50% to 74%</strong></td>
                <td>Moderate</td>
                <td>Candidate has foundational skills but lacks a few key technical tools or domain competencies.</td>
            </tr>
            <tr>
                <td><strong>Below 50%</strong></td>
                <td>Weak</td>
                <td>Significant gaps in required qualifications. Substantial skill acquisition or project work needed first.</td>
            </tr>
        </tbody>
    </table>
    """,
    unsafe_allow_html=True
)

render_footer()
