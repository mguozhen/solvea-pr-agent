#!/usr/bin/env python3
"""
Solvea PR Agent — monitor.py
Checks all submitted press releases for:
- Google indexing status
- Page still live
- New coverage/backlinks via Google search
Run daily via GitHub Actions.
"""
import json, urllib.request, urllib.parse, time
from pathlib import Path
from datetime import datetime

SUBMISSIONS_DIR = Path(__file__).parent.parent / "submissions"

def check_url_live(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=10)
        return r.status == 200
    except:
        return False

def check_google_indexed(url):
    """Check if URL appears in Google search results."""
    query = f"site:{url}"
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(search_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        r = urllib.request.urlopen(req, timeout=10)
        html = r.read().decode("utf-8", errors="ignore")
        return "did not match any documents" not in html.lower()
    except:
        return None  # inconclusive

def check_coverage(title):
    """Search Google for news coverage of the press release."""
    query = f'"{title[:50]}" Solvea'
    search_url = f"https://news.google.com/search?q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(search_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        r = urllib.request.urlopen(req, timeout=10)
        html = r.read().decode("utf-8", errors="ignore")
        # Count approximate hits
        hits = html.count("solvea.cx") + html.lower().count("solvea")
        return {"query": query, "approx_hits": hits, "url": search_url}
    except Exception as e:
        return {"error": str(e)}

def monitor_all():
    results = {}
    submission_files = list(SUBMISSIONS_DIR.glob("*.json"))

    print(f"Monitoring {len(submission_files)} release(s)...\n")

    for sf in submission_files:
        sub = json.loads(sf.read_text())
        stem  = sub["release"]
        title = sub.get("title", stem)
        results[stem] = {"title": title, "platforms": {}}

        print(f"Release: {title}")

        for region, platforms in sub["platforms"].items():
            for platform, data in platforms.items():
                url = data.get("url")
                status = data.get("status")

                if not url or status not in ("submitted", "live"):
                    continue

                live    = check_url_live(url)
                indexed = check_google_indexed(url)

                update = {
                    "url": url,
                    "live": live,
                    "indexed": indexed,
                    "checked_at": datetime.now().isoformat()
                }

                sub["platforms"][region][platform].update(update)
                results[stem]["platforms"][f"{region}/{platform}"] = update

                icon = "✅" if live else "❌"
                idx  = "📑 indexed" if indexed else "⏳ not indexed"
                print(f"  [{region}/{platform}] {icon} live  {idx}  {url}")
                time.sleep(1)

        # Check for news coverage
        coverage = check_coverage(title)
        sub["coverage_check"] = {**coverage, "checked_at": datetime.now().isoformat()}
        print(f"  Coverage search: ~{coverage.get('approx_hits', 0)} hits\n")

        sf.write_text(json.dumps(sub, indent=2, ensure_ascii=False))

    # Write summary
    summary_path = SUBMISSIONS_DIR / "monitor_report.json"
    summary_path.write_text(json.dumps({
        "generated_at": datetime.now().isoformat(),
        "results": results
    }, indent=2, ensure_ascii=False))

    print(f"\nReport saved → {summary_path}")
    return results

if __name__ == "__main__":
    monitor_all()
