# Browser Automation Agent — Claude + Playwright Demo

## What This Does

A working browser automation agent: give it any URL and a task, and it uses Playwright to navigate and screenshot the page, then Claude (with vision) reads the screenshot + page text to complete the task. Runs three preset demos out of the box, or accepts any custom URL and task.

## How It Works

URL + Task → Playwright navigates → Screenshot + page text extracted → Claude vision analyzes → Structured result returned

## Quick Start

```bash
pip install -r requirements.txt
playwright install chromium
export ANTHROPIC_API_KEY=sk-ant-...
streamlit run app.py
```

Then open http://localhost:8501

## Preset Demo Tasks

| Demo | URL | Task |
|------|-----|------|
| Hacker News Top Stories | news.ycombinator.com | Extract top 5 story titles + points |
| PyPI Package Info | pypi.org/project/anthropic | Latest version + release date |
| GitHub Trending | github.com/trending/python | Top 3 trending Python repos |
| Custom | Any URL | Any task |

## Configuration

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Required for Claude vision analysis |

For Streamlit Cloud: add to Settings → Secrets:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

## Streamlit Cloud Note

Playwright requires Chromium to be installed on the host. Add `packages.txt` (included) to install system dependencies on Streamlit Cloud. The `playwright install chromium` command runs automatically via a post-install hook.

## Demo Limitations

This demo handles single-page navigation. A production version would add:
- Multi-step workflows (search → paginate → aggregate)
- Authentication handling (session cookies, OAuth)
- Structured JSON output for downstream systems
- Parallel agent runs across multiple URLs
- n8n integration for scheduled execution
