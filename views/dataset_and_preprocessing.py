"""
Dataset and Preprocessing - Resume-to-Job Gap Analyzer.
Details data provenance, data quality issues discovered, preprocessing stages, and taxonomy structure.
"""

import streamlit as st
import pandas as pd
import altair as alt
from ui_components import apply_theme, render_header, render_footer
from data_loader import (
    load_category_counts,
    load_preprocessing_example,
    load_taxonomy,
    ROOT
)

apply_theme()
render_header()

st.title("Dataset and preprocessing")
st.markdown("<p style='font-size: 1.05rem; color: #4B515D; margin-top: -0.5rem;'>How I cleaned real Kaggle resume data and constructed a synthetic benchmark for evaluation.</p>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# 1. Two data sources
st.subheader("Data sources")
st.markdown(
    """
I used two distinct data sources in this project to separate real-world text cleaning from controlled algorithmic testing:

1. **Kaggle Resume Dataset (Real-world, messy):** Sourced from the public Kaggle resume collection. It contains **962 rows across 25 job categories** (including Data Science, Java Developer, Python Developer, HR, and DevOps). This dataset reflects real-world candidate text, including diverse formatting, varied phrasing, and messy encoding artifacts.
2. **Synthetic Evaluation Set (Synthetic benchmark):** Sourced from 44 custom synthetic resumes, 11 job descriptions, and **88 manually labelled resume-job pairs**. I generated this synthetic corpus specifically to establish unambiguous ground truth for skill extraction and fit scoring without copyright or privacy issues.
    """
)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# 2. Problems found in the raw data
st.subheader("Problems found in the raw data")
st.markdown(
    """
When I profiled the raw Kaggle dataset, I found serious data quality issues that would distort any analysis if left uncorrected:
- **Massive duplication:** 796 of the 962 rows were exact or near-identical duplicates, leaving only 166 unique resumes. In some categories, the same resume appeared 6 to 12 times.
- **Corrupted characters:** 35 rows had broken characters, replacement symbols (`\ufffd`), mojibake quotes, and misencoded bullet points caused by improper character conversions.
- **Unstructured noise:** Resumes contained raw email addresses, personal phone numbers, web links, and irregular whitespace that interfered with word boundary detection.
    """
)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# 3. Preprocessing steps
st.subheader("Preprocessing pipeline")
st.markdown(
    """
I applied a six-step pipeline to clean and normalize the resume corpus:
1. **Load and profile:** Read the raw CSV file and verify column distributions, data types, and null values.
2. **Repair encoding:** Replace replacement characters (`\ufffd`), normalize smart quotes (`\u201c`, `\u201d`), standardize dashes (`\u2013`), and convert bullet points (`\u2022`) into uniform hyphens.
3. **Remove noise:** Strip hyperlinks, email addresses, phone patterns, and arbitrary non-printable symbols using regular expressions.
4. **Lowercase conversion:** Convert all text to lowercase to enable case-insensitive matching across skills.
5. **Drop duplicates:** Eliminate duplicate resumes based on cleaned text hashes, reducing the dataset from **962 rows down to 165 unique resumes**.
6. **Extract skills with taxonomy:** Scan cleaned text for exact terms and synonyms defined in the 73-skill taxonomy using word boundary lookarounds.
    """
)

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# 4. Charts: Rows before/after & categories
st.subheader("Cleaning impact and category distribution")

cat_df, err = load_category_counts()

if cat_df is not None:
    raw_total = int(cat_df["raw_count"].sum())
    clean_total = int(cat_df["clean_count"].sum())
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"**Total rows: raw vs clean**")
        row_comp_df = pd.DataFrame([
            {"Stage": "Raw dataset", "Resumes": raw_total},
            {"Stage": "Clean unique", "Resumes": clean_total}
        ])
        
        row_chart = (
            alt.Chart(row_comp_df)
            .mark_bar(size=36, color="#1B365D")
            .encode(
                x=alt.X("Resumes:Q", title="Number of resumes"),
                y=alt.Y("Stage:N", sort=None, title=""),
                tooltip=["Stage", "Resumes"]
            )
            .properties(height=180)
        )
        st.altair_chart(row_chart, width="stretch")
        st.caption(f"Deduplication removed {raw_total - clean_total} duplicate rows (82.9% reduction).")
        
    with col2:
        st.markdown("**Resumes per category (raw vs cleaned)**")
        # Prepare melted dataframe for grouped bar chart
        melted_cats = cat_df.melt(
            id_vars=["category"],
            value_vars=["raw_count", "clean_count"],
            var_name="Dataset",
            value_name="Count"
        )
        melted_cats["Dataset"] = melted_cats["Dataset"].map({
            "raw_count": "Raw (962 total)",
            "clean_count": "Clean (165 total)"
        })
        
        cat_chart = (
            alt.Chart(melted_cats)
            .mark_bar()
            .encode(
                x=alt.X("Count:Q", title="Number of resumes"),
                y=alt.Y("category:N", sort="-x", title="Job category"),
                color=alt.Color(
                    "Dataset:N",
                    scale=alt.Scale(
                        domain=["Raw (962 total)", "Clean (165 total)"],
                        range=["#8C9BAE", "#1B365D"]
                    ),
                    legend=alt.Legend(orient="bottom", title=None)
                ),
                tooltip=["category", "Dataset", "Count"]
            )
            .properties(height=520)
        )
        st.altair_chart(cat_chart, width="stretch")
else:
    st.info(f"Category counts data unavailable: {err}")

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# 5. Before and after text sample
st.subheader("Text cleaning sample")
st.markdown("Here is an actual resume excerpt before and after running through the cleaning pipeline:")

sample_dict, sample_err = load_preprocessing_example()
if sample_dict is not None:
    c_raw, c_clean = st.columns(2)
    with c_raw:
        st.markdown("**Before cleaning (raw text)**")
        st.code(sample_dict.get("raw", ""), language="text")
    with c_clean:
        st.markdown("**After cleaning (clean tokens)**")
        st.code(sample_dict.get("clean", ""), language="text")
else:
    st.info(f"Preprocessing sample unavailable: {sample_err}")

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# 6. Skills taxonomy table
st.subheader("Skills taxonomy summary")
st.markdown("The gap analyzer maps resume content to a structured taxonomy containing **73 skills** organized across 9 technical and professional categories:")

tax_df, tax_err = load_taxonomy()
if tax_df is not None:
    # Group taxonomy by category
    summary_rows = []
    for cat, group in tax_df.groupby("category"):
        skills_list = group["skill"].tolist()
        summary_rows.append({
            "Category": cat,
            "Skill count": len(skills_list),
            "Skills in taxonomy": ", ".join(skills_list)
        })
    tax_summary_df = pd.DataFrame(summary_rows).sort_values("Skill count", ascending=False)
    
    st.dataframe(
        tax_summary_df,
        column_config={
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Skill count": st.column_config.NumberColumn("Skills", width="small"),
            "Skills in taxonomy": st.column_config.TextColumn("Included skills", width="large"),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info(f"Taxonomy data unavailable: {tax_err}")

render_footer()
