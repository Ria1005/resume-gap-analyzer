"""
Data loader helper for Resume-to-Job Gap Analyzer.
Safely reads metrics, tables, and samples from data/, results/, and project root.
Every function handles missing files gracefully without crashing.
"""

from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).parent


def load_taxonomy(tax_path="skills_taxonomy.csv"):
    """Load skills taxonomy CSV. Returns (DataFrame, None) or (None, error_msg)."""
    p = ROOT / tax_path
    if not p.exists():
        return None, f"File '{tax_path}' not found."
    try:
        df = pd.read_csv(p).fillna("")
        return df, None
    except Exception as e:
        return None, f"Error reading '{tax_path}': {e}"


def load_category_counts(file_path="results/real_category_counts.csv"):
    """Load real vs clean category counts. Returns (DataFrame, None) or (None, error_msg)."""
    p = ROOT / file_path
    if not p.exists():
        return None, f"File '{file_path}' not found."
    try:
        df = pd.read_csv(p)
        return df, None
    except Exception as e:
        return None, f"Error reading '{file_path}': {e}"


def load_preprocessing_example(file_path="results/preprocessing_example.csv"):
    """Load raw vs clean text example. Returns (dict, None) or (None, error_msg)."""
    p = ROOT / file_path
    if not p.exists():
        return None, f"File '{file_path}' not found."
    try:
        df = pd.read_csv(p)
        example_dict = dict(zip(df["stage"], df["text_sample"]))
        return example_dict, None
    except Exception as e:
        return None, f"Error reading '{file_path}': {e}"


def load_model_comparison(file_path="results/model_comparison.csv"):
    """Load model comparison benchmark. Returns (DataFrame, None) or (None, error_msg)."""
    p = ROOT / file_path
    if not p.exists():
        return None, f"File '{file_path}' not found."
    try:
        df = pd.read_csv(p)
        return df, None
    except Exception as e:
        return None, f"Error reading '{file_path}': {e}"


def load_validation_results(file_path="validation_results.csv"):
    """Load validation results CSV for confusion matrix. Returns (DataFrame, None) or (None, error_msg)."""
    p = ROOT / file_path
    if not p.exists():
        return None, f"File '{file_path}' not found."
    try:
        df = pd.read_csv(p)
        return df, None
    except Exception as e:
        return None, f"Error reading '{file_path}': {e}"


def load_validation_report_metrics(file_path="validation_report.txt"):
    """
    Parse key metrics from validation_report.txt.
    Returns (dict, None) or (None, error_msg).
    """
    p = ROOT / file_path
    if not p.exists():
        return None, f"File '{file_path}' not found."
    try:
        text = p.read_text(encoding="utf-8")
        metrics = {
            "num_resumes": None,
            "skill_precision": None,
            "skill_recall": None,
            "skill_f1": None,
            "all_fit_accuracy": None,
            "all_mean_error": None,
            "all_within_10": None,
            "all_correlation": None,
            "test_fit_accuracy": None,
            "test_mean_error": None,
            "raw_text": text
        }
        
        # Skill extraction line: Precision 96.3%   Recall 94.2%   F1 95.2%
        m_skill = re.search(r"Precision\s+([\d\.]+)%\s+Recall\s+([\d\.]+)%\s+F1\s+([\d\.]+)%", text)
        if m_skill:
            metrics["skill_precision"] = float(m_skill.group(1))
            metrics["skill_recall"] = float(m_skill.group(2))
            metrics["skill_f1"] = float(m_skill.group(3))
            
        m_res = re.search(r"Skill extraction from resumes \((\d+) resumes\)", text)
        if m_res:
            metrics["num_resumes"] = int(m_res.group(1))
            
        # Fit label accuracy (All)
        m_all_acc = re.search(r"All \(\d+ pairs\)\s+Fit label accuracy [^:]+:\s+([\d\.]+)%", text)
        if m_all_acc:
            metrics["all_fit_accuracy"] = float(m_all_acc.group(1))
            
        m_all_score = re.search(r"All \(\d+ pairs\).*?Score: mean error ([\d\.]+) points, within 10 points: ([\d\.]+)%, correlation ([\d\.]+)", text, re.S)
        if m_all_score:
            metrics["all_mean_error"] = float(m_all_score.group(1))
            metrics["all_within_10"] = float(m_all_score.group(2))
            metrics["all_correlation"] = float(m_all_score.group(3))
            
        # Test set
        m_test_acc = re.search(r"Test set only \(\d+ pairs\)\s+Fit label accuracy [^:]+:\s+([\d\.]+)%", text)
        if m_test_acc:
            metrics["test_fit_accuracy"] = float(m_test_acc.group(1))
            
        m_test_score = re.search(r"Test set only \(\d+ pairs\).*?Score: mean error ([\d\.]+) points, within 10 points: ([\d\.]+)%, correlation ([\d\.]+)", text, re.S)
        if m_test_score:
            metrics["test_mean_error"] = float(m_test_score.group(1))
            metrics["test_within_10"] = float(m_test_score.group(2))
            metrics["test_correlation"] = float(m_test_score.group(3))
            
        return metrics, None
    except Exception as e:
        return None, f"Error reading '{file_path}': {e}"


def load_dataset_summary():
    """
    Load high-level summary counts from data/ and skills_taxonomy.csv.
    Returns (dict, list_of_warnings).
    """
    summary = {
        "num_skills": 73,
        "num_resumes": 44,
        "num_jds": 11,
        "num_pairs": 88,
        "skill_f1": 95.2,
        "fit_accuracy": 90.9
    }
    warnings = []
    
    # Check taxonomy
    tax_df, err = load_taxonomy()
    if tax_df is not None:
        summary["num_skills"] = len(tax_df)
    else:
        warnings.append(err)
        
    # Check resumes
    res_path = ROOT / "data" / "resumes.csv"
    if res_path.exists():
        try:
            summary["num_resumes"] = len(pd.read_csv(res_path))
        except Exception as e:
            warnings.append(f"Error reading 'data/resumes.csv': {e}")
    else:
        warnings.append("File 'data/resumes.csv' not found.")
        
    # Check JDs
    jd_path = ROOT / "data" / "job_descriptions.csv"
    if jd_path.exists():
        try:
            summary["num_jds"] = len(pd.read_csv(jd_path))
        except Exception as e:
            warnings.append(f"Error reading 'data/job_descriptions.csv': {e}")
    else:
        warnings.append("File 'data/job_descriptions.csv' not found.")

    # Check pairs
    pairs_path = ROOT / "data" / "pair_labels.csv"
    if pairs_path.exists():
        try:
            summary["num_pairs"] = len(pd.read_csv(pairs_path))
        except Exception as e:
            warnings.append(f"Error reading 'data/pair_labels.csv': {e}")
    else:
        warnings.append("File 'data/pair_labels.csv' not found.")
        
    # Check validation report
    val_metrics, err = load_validation_report_metrics()
    if val_metrics is not None:
        if val_metrics.get("skill_f1") is not None:
            summary["skill_f1"] = val_metrics["skill_f1"]
        if val_metrics.get("all_fit_accuracy") is not None:
            summary["fit_accuracy"] = val_metrics["all_fit_accuracy"]
    else:
        warnings.append(err)

    return summary, warnings
