"""
Automated screenshot generator for Resume-to-Job Gap Analyzer.
Starts Streamlit and uses headless browser to capture screenshots of all 5 pages.
"""

from pathlib import Path
import subprocess
import time
import urllib.request
import os

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

browser_exe = EDGE_PATH if os.path.exists(EDGE_PATH) else CHROME_PATH

screenshots_dir = Path("screenshots")
screenshots_dir.mkdir(exist_ok=True)

pages = [
    ("1_home.png", "http://localhost:8501/"),
    ("2_how_to_use.png", "http://localhost:8501/how-to-use"),
    ("3_dataset_and_preprocessing.png", "http://localhost:8501/dataset-and-preprocessing"),
    ("4_analyzer.png", "http://localhost:8501/analyzer?sample=true"),
    ("5_results_and_limits.png", "http://localhost:8501/results-and-limits"),
]

print("Starting Streamlit server...")
server_cmd = [
    "python", "-m", "streamlit", "run", "app.py",
    "--server.port=8501",
    "--server.headless=true",
    "--browser.gatherUsageStats=false"
]

server_proc = subprocess.Popen(server_cmd)

try:
    # Wait for server to respond
    ready = False
    for i in range(25):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://localhost:8501/healthz", timeout=2) as resp:
                if resp.status == 200:
                    ready = True
                    print("Streamlit server is ready!")
                    break
        except Exception:
            pass

    if not ready:
        # Try checking root URL
        for i in range(10):
            time.sleep(1)
            try:
                with urllib.request.urlopen("http://localhost:8501/", timeout=2) as resp:
                    ready = True
                    print("Streamlit server is ready on root URL!")
                    break
            except Exception:
                pass

    if not ready:
        raise RuntimeError("Streamlit server failed to start within timeout.")

    # Capture screenshots
    for fname, url in pages:
        out_path = screenshots_dir / fname
        print(f"Capturing {fname} from {url}...")
        cmd = [
            browser_exe,
            "--headless",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1280,1050",
            "--virtual-time-budget=7000",
            f"--screenshot={out_path.resolve()}",
            url
        ]
        res = subprocess.run(cmd, capture_output=True, timeout=25)
        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"  Saved {fname} ({out_path.stat().st_size / 1024:.1f} KB)")
        else:
            print(f"  Warning: {fname} was not created. Stderr: {res.stderr.decode('utf-8', errors='replace')}")

    print("All screenshots generated successfully.")

finally:
    print("Stopping Streamlit server...")
    server_proc.terminate()
    try:
        server_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_proc.kill()
    print("Done.")
