# Solvea PR Agent

Auto-submit press releases to free distribution platforms and monitor coverage.

## Workflow

1. **Add a release** → drop a `.md` file into `releases/`
   - English: `YYYY-MM-DD-slug-en.md`
   - Japanese: `YYYY-MM-DD-slug-jp.md`
2. **GitHub Actions triggers** → `submit.yml` auto-submits to all platforms
3. **Daily monitor** → `monitor.yml` checks indexing & coverage, reports to DingTalk

## Platforms

| Region | Platform | Free | Status |
|--------|----------|------|--------|
| 🇺🇸 US | PRLog | ✅ | active |
| 🇺🇸 US | OpenPR | ✅ | active |
| 🇺🇸 US | PR.com | ✅ | active |
| 🇺🇸 US | 1888PressRelease | ✅ | active |
| 🇺🇸 US | PRFree | ✅ | active |
| 🇺🇸 US | NewswireToday | ✅ | active |
| 🇺🇸 US | PR Underground | ✅ | active |
| 🇯🇵 JP | Dreamnews | ✅ | active |
| 🇯🇵 JP | ValuePress | ✅ | active |
| 🇯🇵 JP | @Press | ✅ | active |
| 🇯🇵 JP | PRTREE | ✅ | active |

## Secrets Required (GitHub → Settings → Secrets)

| Secret | Value |
|--------|-------|
| `PR_ACCOUNT_EMAIL` | boyuan@solvea.cx |
| `PR_ACCOUNT_PASSWORD` | Solvea@2025! |
| `DINGTALK_APP_KEY` | ding3shkntgajgeigymb |
| `DINGTALK_APP_SECRET` | f2GBQzDl_... |
| `DINGTALK_CONV_ID` | cid13BaabhcPB/tVfF10dwfyA== |

## Manual Submit

```bash
python3 scripts/submit_all.py releases/2026-04-03-ai-receptionist-launch-en.md
python3 scripts/submit_all.py releases/2026-04-03-ai-receptionist-launch-jp.md
```

## Monitor

```bash
python3 scripts/monitor.py
cat submissions/monitor_report.json
```
