#!/usr/bin/env python3
"""
Solvea PR Agent — submit_all.py
Reads a release markdown file and submits to all configured platforms.
Usage: python3 submit_all.py releases/2026-04-03-ai-receptionist-launch-en.md
"""
import sys, json, time, subprocess
from pathlib import Path
from datetime import datetime

SUBMISSIONS_DIR = Path(__file__).parent.parent / "submissions"
PLATFORMS_DIR   = Path(__file__).parent.parent / "platforms"

ACCOUNT_EMAIL    = "boyuan@solvea.cx"
ACCOUNT_PASSWORD = "Solvea@2025!"
ACCOUNT_NAME     = "Bo Yuan"
ACCOUNT_COMPANY  = "Solvea"
ACCOUNT_URL      = "https://solvea.cx"

US_PLATFORMS = [
    "prlog",
    "openpr",
    "pr_com",
    "1888press",
    "prfree",
    "newswiretoday",
    "prunderground",
]

JP_PLATFORMS = [
    "dreamnews",
    "valupress",
    "atpress",
    "prtree",
]

def load_release(path):
    content = Path(path).read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    title = ""
    for line in lines:
        line = line.strip()
        if line.startswith("**") and "Solvea" in line:
            title = line.replace("**", "").strip()
            break
    return {"title": title, "body": content}

def submit_platform(platform, release, lang="en"):
    script = PLATFORMS_DIR / lang_to_dir(lang) / f"{platform}.py"
    if not script.exists():
        return {"status": "no_script", "error": f"{script} not found"}
    try:
        result = subprocess.run(
            ["python3", str(script)],
            input=json.dumps({"release": release, "email": ACCOUNT_EMAIL,
                              "password": ACCOUNT_PASSWORD, "name": ACCOUNT_NAME,
                              "company": ACCOUNT_COMPANY, "url": ACCOUNT_URL}),
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"status": "failed", "error": result.stderr[:200]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def lang_to_dir(lang):
    return "us" if lang == "en" else "jp"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 submit_all.py <release_file>")
        sys.exit(1)

    release_path = sys.argv[1]
    lang = "jp" if release_path.endswith("-jp.md") else "en"
    platforms = JP_PLATFORMS if lang == "jp" else US_PLATFORMS

    release = load_release(release_path)
    stem = Path(release_path).stem.replace("-en", "").replace("-jp", "")
    submission_file = SUBMISSIONS_DIR / f"{stem}.json"

    if submission_file.exists():
        submission = json.loads(submission_file.read_text())
    else:
        submission = {"release": stem, "title": release["title"],
                      "submitted_at": datetime.now().strftime("%Y-%m-%d"),
                      "platforms": {"us": {}, "jp": {}}}

    region = "jp" if lang == "jp" else "us"
    print(f"\nSubmitting {stem} ({lang.upper()}) to {len(platforms)} platforms...\n")

    for platform in platforms:
        current = submission["platforms"][region].get(platform, {})
        if current.get("status") in ("submitted", "live"):
            print(f"  [{platform}] already submitted — skipping")
            continue

        print(f"  [{platform}] submitting...", end=" ", flush=True)
        result = submit_platform(platform, release, lang)
        submission["platforms"][region][platform] = {
            **result,
            "attempted_at": datetime.now().isoformat()
        }
        submission_file.write_text(json.dumps(submission, indent=2, ensure_ascii=False))

        status = result.get("status", "unknown")
        url    = result.get("url", "")
        print(f"{'✅' if status == 'submitted' else '❌'} {status} {url}")
        time.sleep(3)

    print(f"\nDone. Results saved → {submission_file}")

if __name__ == "__main__":
    main()
