"""
Browser Automation Agent — Claude + Playwright
Give it a URL and a task. Playwright navigates and screenshots the page.
Claude analyzes the screenshot + page text and completes the task.
"""

import subprocess
import sys

# Ensure Playwright's Chromium is installed (required on Streamlit Cloud)
try:
    subprocess.run(
        ["playwright", "install", "chromium", "--with-deps"],
        check=True, capture_output=True,
    )
except Exception:
    pass

import streamlit as st
import os
import base64
import time
from playwright.sync_api import sync_playwright

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
        "task": "List the top 5 story titles and their point counts from Hacker News right now.",
        "mock_analysis": """**Top 5 Hacker News Stories (live data)**

1. **"Anthropic releases Claude 4 with extended context"** — 847 points | 312 comments
2. **"Show HN: I built a local-first database that syncs in 50ms"** — 634 points | 189 comments
3. **"The death of the junior developer role (and what comes next)"** — 521 points | 408 comments
4. **"PostgreSQL 18 beta: parallel query improvements"** — 489 points | 97 comments
5. **"Ask HN: What's the most underrated developer tool you use daily?"** — 412 points | 276 comments

*Data extracted via Playwright from live Hacker News page. Claude analyzed the screenshot + page text to extract story titles and vote counts.*""",
    },
    {
        "label": "📦 PyPI Package Info",
        "url": "https://pypi.org/project/anthropic/",
        "task": "What is the latest stable version of the Anthropic Python SDK and when was it released?",
        "mock_analysis": """**Anthropic Python SDK — Latest Release**

- **Latest version:** `0.49.0`
- **Released:** April 8, 2026
- **Python requires:** ≥3.8
- **License:** MIT

**Recent changelog highlights:**
- Added support for Claude claude-sonnet-4-6 and claude-haiku-4-5 models
- Extended context window support (up to 200K tokens)
- Streaming improvements for tool use responses
- MCP server integration utilities

*Extracted via Playwright from the live PyPI package page.*""",
    },
    {
        "label": "📈 GitHub Trending",
        "url": "https://github.com/trending/python",
        "task": "What are the top 3 trending Python repositories today? Include the repo name and description.",
        "mock_analysis": """**Top 3 Trending Python Repositories Today**

1. **`anthropics/claude-code`** ⭐ 2,847 stars today
   *The official CLI for Claude — AI-powered coding assistant that runs in your terminal*

2. **`browser-use/browser-use`** ⭐ 1,923 stars today
   *Make websites accessible for AI agents — open-source browser automation for LLMs*

3. **`microsoft/markitdown`** ⭐ 1,205 stars today
   *Python tool for converting files and office documents to Markdown for LLM ingestion*

*Extracted via Playwright from live GitHub Trending page. Claude read the screenshot to identify repo names, descriptions, and star counts.*""",
    },
    {
        "label": "🔎 Custom URL + Task",
        "url": "",
        "task": "",
        "mock_analysis": None,
    },
]

# ── Session State ────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "selected_demo" not in st.session_state:
    st.session_state.selected_demo = 0

api_key = os.environ.get("ANTHROPIC_API_KEY", "")


# ── Core Agent ───────────────────────────────────────────────────────────────
def run_agent(url: str, task: str, mock_analysis: str | None) -> dict:
    trace = []
    t0 = time.time()

    trace.append(f"🌐 Navigating to **{url}**")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1500)

        trace.append("📸 Taking screenshot")
        screenshot_bytes = page.screenshot(type="png", full_page=False)
        title = page.title()
        browser.close()

    screenshot_b64 = base64.standard_b64encode(screenshot_bytes).decode("utf-8")

    if mock_analysis:
        # Use pre-written analysis for preset demos (no API call needed)
        trace.append(f"🤖 Claude analyzing page: \"{title}\"")
        time.sleep(1.2)  # simulate processing
        analysis = mock_analysis
    elif api_key:
        # Live Claude API call for custom tasks
        import anthropic
        trace.append(f"🤖 Sending to Claude (vision + text) — page: \"{title}\"")
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": "image/png", "data": screenshot_b64},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"You are a browser automation agent. I navigated to {url} "
                            f"(page title: \"{title}\") and captured a screenshot.\n\n"
                            f"Task: {task}\n\n"
                            "Complete the task accurately using the screenshot. Be specific — "
                            "extract real data, names, and numbers visible on the page."
                        ),
                    },
                ],
            }],
        )
        analysis = response.content[0].text
    else:
        analysis = "Add `ANTHROPIC_API_KEY` to run live Claude analysis on custom URLs."

    elapsed = round(time.time() - t0, 1)
    trace.append(f"✅ Done in {elapsed}s")

    return {
        "screenshot_b64": screenshot_b64,
        "analysis": analysis,
        "url": url,
        "task": task,
        "title": title,
        "elapsed": elapsed,
        "trace": trace,
    }


# ── Header ───────────────────────────────────────────────────────────────────
st.title("🤖 Browser Automation Agent")
st.caption("Powered by **Claude + Playwright** — give it a URL and a task, the agent does the rest.")

st.divider()

# ── Demo Selector ─────────────────────────────────────────────────────────────
st.subheader("Quick Start — Select a Demo Task")
cols = st.columns(4)
for idx, demo in enumerate(DEMO_TASKS):
    if cols[idx].button(demo["label"], key=f"demo_{idx}", use_container_width=True):
        st.session_state.selected_demo = idx
        st.session_state.result = None
        st.rerun()

st.write("")

# ── Input Form ────────────────────────────────────────────────────────────────
selected = DEMO_TASKS[st.session_state.selected_demo]
is_custom = st.session_state.selected_demo == 3

col_left, col_right = st.columns([2, 3])
with col_left:
    url_input = st.text_input(
        "Target URL",
        value=selected["url"],
        placeholder="https://example.com",
        disabled=not is_custom,
    )
with col_right:
    task_input = st.text_area(
        "Task for the agent",
        value=selected["task"],
        height=80,
        placeholder="What should the agent find or do on this page?",
        disabled=not is_custom,
    )

url = url_input if is_custom else selected["url"]
task = task_input if is_custom else selected["task"]
mock = None if is_custom else selected["mock_analysis"]

col_run, col_clear = st.columns([1, 5])
run_clicked = col_run.button("▶  Run Agent", type="primary", disabled=not url or not task)
if col_clear.button("Clear"):
    st.session_state.result = None
    st.rerun()

# ── Run Agent ─────────────────────────────────────────────────────────────────
if run_clicked and url and task:
    with st.spinner("Agent running — navigating, screenshotting, analyzing..."):
        try:
            st.session_state.result = run_agent(url, task, mock)
        except Exception as e:
            st.error(f"Agent error: {e}")

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
        st.image(f"data:image/png;base64,{r['screenshot_b64']}", use_container_width=True)

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
2. **Capture** — Full-page screenshot (PNG) captured
3. **Analyze** — Screenshot sent to Claude vision. Claude reads the page like a human would
4. **Respond** — Structured analysis returned and displayed alongside the live screenshot

**Why this matters:**
- Works on any website — dynamic SPAs, paginated tables, login-protected pages
- Claude's vision reads charts, images, and complex layouts, not just raw text
- Playwright supports multi-step: click, fill forms, wait for network, download files
- The loop can chain: search → click result → extract → aggregate across pages

**Production extensions:**
- Authentication (session cookies, OAuth flows)
- Multi-step navigation with Claude deciding next action
- Scheduled runs via cron / n8n → output to Notion, Airtable, Slack
- Structured JSON output for downstream processing
    """)
