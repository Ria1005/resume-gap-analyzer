"""
UI components and styling helpers for Resume-to-Job Gap Analyzer.
Maintains a clean, hand-crafted, editorial visual identity:
- Serif headings ('Lora') and clean sans-serif body ('Inter')
- Calm neutral palette (paper background, subtle borders, deep navy accent)
- No emojis in headings or tags
- Consistent headers and footers with logo support
"""

from pathlib import Path
import streamlit as st
import site_config

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap');

/* Global typography */
html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #24272C;
}

/* Preserve Streamlit icon font and prevent ligature text leakage like 'uploadpload' */
[data-testid="stIcon"],
[class*="material-symbols"],
[class*="material-icons"],
span[class*="material-symbols"],
[data-testid="stFileUploader"] span[class*="material"] {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}

h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"] *,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
.stHeadingContainer h1,
.stHeadingContainer h2,
.stHeadingContainer h3 {
    font-family: 'Lora', Georgia, 'Times New Roman', serif !important;
    color: #142236 !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}

/* Hide default streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* Hide Fork button, GitHub links, and toolbar actions from top-right header while keeping navbar */
[data-testid="stHeaderActionElements"],
[data-testid="stToolbarActions"],
.stAppDeployButton,
header a[href*="github.com"],
header a[href*="fork"],
header button[title*="Fork"],
header a[title*="GitHub"],
header div:has(> a[href*="github.com"]) {
    display: none !important;
    visibility: hidden !important;
}

/* Ensure top navigation bar remains completely visible and left-aligned */
[data-testid="stTopNav"],
nav[data-testid="stTopNav"],
header [data-testid="stTopNav"] {
    display: flex !important;
    visibility: visible !important;
}

/* Constrain main block width for reading comfort */
.block-container {
    max-width: 960px;
    padding-top: 1.5rem;
    padding-bottom: 6rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

/* Normal button styling */
div.stButton > button {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    border-radius: 4px;
    padding: 0.45rem 1rem;
    box-shadow: none !important;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}

div.stButton > button[kind="primary"] {
    background-color: #1B365D !important;
    color: #FFFFFF !important;
    border: 1px solid #1B365D !important;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #132742 !important;
    border-color: #132742 !important;
}

div.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #24272C !important;
    border: 1px solid #D5D1C8 !important;
}

div.stButton > button[kind="secondary"]:hover {
    background-color: #F4F2EC !important;
    border-color: #BCB6A9 !important;
}

/* Download button */
div.stDownloadButton > button {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    border-radius: 4px;
    padding: 0.45rem 1rem;
    background-color: #FFFFFF !important;
    color: #1B365D !important;
    border: 1px solid #1B365D !important;
    box-shadow: none !important;
}

div.stDownloadButton > button:hover {
    background-color: #F0F4FA !important;
}

/* Input fields */
div[data-baseweb="input"], div[data-baseweb="textarea"] {
    border-radius: 4px !important;
    border: 1px solid #D5D1C8 !important;
    background-color: #FFFFFF !important;
}

/* Metric styling */
div[data-testid="stMetricValue"] {
    font-family: 'Lora', Georgia, serif !important;
    font-size: 2rem !important;
    color: #142236 !important;
}

div[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #5E646E !important;
}

/* Custom editorial components */
.stat-box {
    background: #FFFFFF;
    border: 1px solid #E2DED5;
    border-radius: 4px;
    padding: 1rem 1.25rem;
    text-align: left;
}

.stat-num {
    font-family: 'Lora', Georgia, serif;
    font-size: 1.9rem;
    font-weight: 600;
    color: #1B365D;
    line-height: 1.1;
}

.stat-label {
    font-size: 0.85rem;
    color: #555A62;
    margin-top: 0.35rem;
    line-height: 1.3;
}

/* Skill tags */
.tag-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
    margin-bottom: 12px;
}

.skill-tag {
    display: inline-block;
    padding: 3px 9px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 3px;
    line-height: 1.4;
}

.tag-have {
    background-color: #EDF4EE;
    border: 1px solid #BCD3BF;
    color: #1E4627;
}

.tag-partial {
    background-color: #FDF4E7;
    border: 1px solid #E7D1A8;
    color: #6C4410;
}

.tag-missing {
    background-color: #F9ECEB;
    border: 1px solid #E7BDBB;
    color: #722320;
}

.tag-neutral {
    background-color: #F1EFEA;
    border: 1px solid #D8D4CC;
    color: #383B40;
}

/* Editorial note box */
.info-note {
    background-color: #F6F5F1;
    border-left: 3px solid #1B365D;
    padding: 0.85rem 1.1rem;
    border-radius: 0 4px 4px 0;
    font-size: 0.92rem;
    color: #2F3338;
    margin: 1rem 0;
}

/* Step list */
.step-item {
    margin-bottom: 1.25rem;
}
.step-num {
    font-family: 'Lora', Georgia, serif;
    font-weight: 600;
    font-size: 1.1rem;
    color: #1B365D;
    margin-bottom: 0.2rem;
}
.step-desc {
    font-size: 0.95rem;
    color: #33363B;
    line-height: 1.5;
}

/* Page footer */
.page-footer {
    margin-top: 3.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid #E2DED5;
    font-size: 0.85rem;
    color: #656A72;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 2.5rem;
}

/* Tables */
table.plain-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.92rem;
    margin: 1rem 0;
}

table.plain-table th {
    text-align: left;
    padding: 8px 12px;
    border-bottom: 2px solid #1B365D;
    color: #142236;
    font-weight: 600;
}

table.plain-table td {
    padding: 8px 12px;
    border-bottom: 1px solid #E5E1D8;
    color: #2E3238;
}

table.plain-table tr:hover td {
    background-color: #F8F7F3;
}
</style>
"""


def apply_theme():
    """Inject custom editorial CSS."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header():
    """Render subtle header with logo if present, skipped quietly if missing."""
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        c1, c2 = st.columns([1, 8])
        with c1:
            st.image(str(logo_path), width=64)
        with c2:
            st.markdown(
                f"<div style='padding-top: 8px; font-family: Lora, serif; font-size: 1.15rem; color: #1B365D; font-weight: 600;'>"
                f"{site_config.PROJECT}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)


def render_footer():
    """Render subtle footer on every page."""
    # Only show author details if configured with real values (not default placeholders)
    has_name = site_config.NAME and not site_config.NAME.strip().startswith("[")
    has_enroll = site_config.ENROLLMENT and not site_config.ENROLLMENT.strip().startswith("[")
    
    author_parts = []
    if has_name:
        author_parts.append(site_config.NAME.strip())
    if has_enroll:
        author_parts.append(f"({site_config.ENROLLMENT.strip()})")
    
    author_str = f" &middot; {' '.join(author_parts)}" if author_parts else ""

    st.markdown(
        f"""
        <div class="page-footer">
            <div>
                <strong>{site_config.PROJECT}</strong>{author_str}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tag_list(tags, tag_type="have", fallback="None"):
    """Render small colored tags without emojis."""
    if not tags:
        st.markdown(f"<span style='color: #6A6E75; font-size: 0.9rem;'>{fallback}</span>", unsafe_allow_html=True)
        return
    
    html = ['<div class="tag-container">']
    for t in tags:
        html.append(f'<span class="skill-tag tag-{tag_type}">{t}</span>')
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)
