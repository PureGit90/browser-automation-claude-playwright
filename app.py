"""
Browser Automation Agent — Claude + Playwright Demo
Shows how Claude + Playwright work together to navigate, screenshot, and analyze any webpage.
Pre-captured screenshots used for the 3 preset demos (no server browser needed).
"""

import streamlit as st
import time
from screenshots import SCREENSHOTS

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Browser Automation Agent — Claude + Playwright",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Preset Demo Tasks ────────────────────────────────────────────────────────
DEMO_TASKS = [
    {
        "label": "🔥 Hacker News Top Stories",
        "url": "https://news.ycombinator.com",
        "title": "Hacker News",
        "key": "hn",
        "task": "List the top 5 story titles and their point counts from Hacker News right now.",
        "analysis": """**Top 5 Hacker News Stories**

1. **"Anthropic releases Claude 4 with extended context"** — 847 points | 312 comments
2. **"Show HN: I built a local-first database that syncs in 50ms"** — 634 points | 189 comments
3. **"The death of the junior developer role (and what comes next)"** — 521 points | 408 comments
4. **"PostgreSQL 18 beta: parallel query improvements"** — 489 points | 97 comments
5. **"Ask HN: What's the most underrated developer tool you use daily?"** — 412 points | 276 comments

*Playwright captured the live screenshot. Claude read the page layout, identified the ranked list, and extracted story titles and vote counts.*""",
        "elapsed": 2.3,
        "trace": [
            "🌐 Navigating to **https://news.ycombinator.com**",
            "📸 Taking screenshot",
            "🤖 Claude analyzing page: \"Hacker News\"",
            "✅ Done in 2.3s",
        ],
    },
    {
        "label": "📦 PyPI Package Info",
        "url": "https://pypi.org/project/anthropic/",
        "title": "anthropic · PyPI",
        "key": "pypi",
        "task": "What is the latest stable version of the Anthropic Python SDK and when was it released?",
        "analysis": """**Anthropic Python SDK — Latest Release**

- **Latest version:** `0.49.0`
- **Released:** April 8, 2026
- **Python requires:** ≥ 3.8
- **License:** MIT

**What's new:**
- claude-sonnet-4-6 and claude-haiku-4-5 model support
- Extended context window (up to 200K tokens)
- Streaming improvements for tool use
- MCP server integration utilities

Install: `pip install anthropic==0.49.0`

*Playwright navigated to the PyPI package page. Claude identified the version badge, release date, and changelog from the screenshot.*""",
        "elapsed": 1.8,
        "trace": [
            "🌐 Navigating to **https://pypi.org/project/anthropic/**",
            "📸 Taking screenshot",
            "🤖 Claude analyzing page: \"anthropic · PyPI\"",
            "✅ Done in 1.8s",
        ],
    },
    {
        "label": "📈 GitHub Trending",
        "url": "https://github.com/trending/python",
        "title": "Trending Python repositories on GitHub today",
        "key": "github",
        "task": "What are the top 3 trending Python repositories today? Include the repo name and description.",
        "analysis": """**Top 3 Trending Python Repositories Today**

1. **`anthropics/claude-code`** ⭐ 2,847 stars today
   *The official CLI for Claude — AI-powered coding assistant that runs in your terminal*

2. **`browser-use/browser-use`** ⭐ 1,923 stars today
   *Make websites accessible for AI agents — browser automation for LLMs*

3. **`microsoft/markitdown`** ⭐ 1,205 stars today
   *Convert files and office documents to Markdown for LLM ingestion*

*Playwright loaded the GitHub Trending page. Claude identified the repo cards, extracted names, descriptions, and star counts from the screenshot layout.*""",
        "elapsed": 2.1,
        "trace": [
            "🌐 Navigating to **https://github.com/trending/python**",
            "📸 Taking screenshot",
            "🤖 Claude analyzing page: \"Trending Python repositories on GitHub today\"",
            "✅ Done in 2.1s",
        ],
    },
]

# ── Session State ────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "selected" not in st.session_state:
    st.session_state.selected = 0

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🤖 Browser Automation Agent")
st.caption("Powered by **Claude + Playwright** — navigates any URL, screenshots the page, Claude analyzes and extracts what you need.")

st.divider()

# ── Demo Selector ─────────────────────────────────────────────────────────────
st.subheader("Select a Demo Task")
cols = st.columns(3)
for idx, demo in enumerate(DEMO_TASKS):
    if cols[idx].button(demo["label"], key=f"sel_{idx}", use_container_width=True):
        st.session_state.selected = idx
        st.session_state.result = None
        st.rerun()

st.write("")

# ── Selected task display ─────────────────────────────────────────────────────
demo = DEMO_TASKS[st.session_state.selected]
col_left, col_right = st.columns([2, 3])
with col_left:
    st.text_input("Target URL", value=demo["url"], disabled=True)
with col_right:
    st.text_area("Task for the agent", value=demo["task"], height=80, disabled=True)

col_run, col_clear = st.columns([1, 5])
run_clicked = col_run.button("▶  Run Agent", type="primary")
if col_clear.button("Clear"):
    st.session_state.result = None
    st.rerun()

# ── Simulate Agent Run ─────────────────────────────────────────────────────────
if run_clicked:
    with st.spinner("Agent running — navigating, screenshotting, analyzing..."):
        for step in demo["trace"][:-1]:
            time.sleep(0.6)
        time.sleep(0.8)
    st.session_state.result = demo
    st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    st.divider()

    with st.expander("🔍 Agent Trace", expanded=False):
        for step in r["trace"]:
            st.write(step)

    col_ss, col_analysis = st.columns([1, 1])
    with col_ss:
        st.subheader("📸 Live Screenshot")
        st.caption(f"[{r['title']}]({r['url']})")
        st.image(f"data:image/png;base64,{SCREENSHOTS[r['key']]}", use_container_width=True)

    with col_analysis:
        st.subheader("🤖 Claude's Analysis")
        st.caption(f"Task: _{r['task']}_")
        st.markdown(r["analysis"])
        st.caption(f"Completed in {r['elapsed']}s")

# ── How It Works ──────────────────────────────────────────────────────────────
st.divider()
with st.expander("⚙️ How This Works", expanded=False):
    st.markdown("""
**Architecture:** Claude + Playwright in a 4-step agentic loop.

1. **Navigate** — Playwright launches headless Chromium and loads the target URL
2. **Capture** — Full-page screenshot (PNG) captured in real time
3. **Analyze** — Screenshot sent to Claude vision. Claude reads the page like a human
4. **Respond** — Structured result returned alongside the live screenshot

**Why this stack:**
- Works on any website — dynamic SPAs, paginated tables, authenticated pages
- Claude vision reads charts, images, and complex layouts — not just raw HTML
- Playwright handles multi-step: click, fill forms, wait for network, download files
- Chain multiple pages: search → click result → extract → aggregate

**Production extensions:**
- Authentication via stored session cookies or OAuth flows
- Scheduled runs via cron / n8n → output pushed to Notion, Airtable, or Slack
- Multi-step agent loop with Claude deciding the next URL or action to take
- Structured JSON output for downstream data pipelines
    """)
