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
        check=True,
        capture_output=True,
    )
except Exception:
    pass

import streamlit as st
import anthropic
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
    },
    {
        "label": "📦 PyPI Package Info",
        "url": "https://pypi.org/project/anthropic/",
        "task": "What is the latest stable version of the Anthropic Python SDK and when was it released?",
    },
    {
        "label": "📈 GitHub Trending",
        "url": "https://github.com/trending/python",
        "task": "What are the top 3 trending Python repositories today? Include the repo name and description.",
    },
    {
        "label": "🔎 Custom URL + Task",
        "url": "",
        "task": "",
    },
]

# ── Session State ────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "trace" not in st.session_state:
    st.session_state.trace = []
if "selected_demo" not in st.session_state:
    st.session_state.selected_demo = 0

# ── API Key ──────────────────────────────────────────────────────────────────
api_key = os.environ.get("ANTHROPIC_API_KEY", "")


# ── Core Agent ───────────────────────────────────────────────────────────────
def run_agent(url: str, task: str) -> dict:
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

        trace.append("📄 Extracting page text")
        try:
            text_content = page.evaluate("() => document.body.innerText").strip()
        except Exception:
            text_content = ""
        text_content = text_content[:4000]

        title = page.title()
        browser.close()

    screenshot_b64 = base64.standard_b64encode(screenshot_bytes).decode("utf-8")
    trace.append(f"🤖 Sending to Claude (vision + text) — page: \"{title}\"")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_b64,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        f"You are a browser automation agent. I navigated to {url} (page title: \"{title}\") "
                        f"and captured a screenshot.\n\n"
                        f"Page text extract (first 4000 chars):\n{text_content}\n\n"
                        f"Task: {task}\n\n"
                        "Complete the task accurately using both the screenshot and the page text. "
                        "Be specific — extract real data, names, numbers, and links visible on the page. "
                        "Format your response clearly."
                    ),
                },
            ],
        }],
    )

    elapsed = round(time.time() - t0, 1)
    trace.append(f"✅ Done in {elapsed}s")

    return {
        "screenshot_b64": screenshot_b64,
        "analysis": response.content[0].text,
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

col_run, col_clear = st.columns([1, 5])
with col_run:
    run_clicked = st.button("▶  Run Agent", type="primary", disabled=not api_key or not url or not task)

if not api_key:
    st.warning("Add **ANTHROPIC_API_KEY** to environment or Streamlit secrets to run the agent.")

if col_clear.button("Clear"):
    st.session_state.result = None
    st.session_state.trace = []
    st.rerun()

# ── Run Agent ─────────────────────────────────────────────────────────────────
if run_clicked and url and task:
    with st.spinner("Agent running — navigating, screenshotting, analyzing..."):
        try:
            result = run_agent(url, task)
            st.session_state.result = result
            st.session_state.trace = result["trace"]
        except Exception as e:
            st.error(f"Agent error: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    st.divider()

    # Trace
    with st.expander("🔍 Agent Trace", expanded=False):
        for step in r["trace"]:
            st.write(step)

    # Side-by-side: screenshot + analysis
    col_ss, col_analysis = st.columns([1, 1])

    with col_ss:
        st.subheader("📸 Screenshot")
        st.caption(f"[{r['title']}]({r['url']})")
        st.image(
            f"data:image/png;base64,{r['screenshot_b64']}",
            use_container_width=True,
        )

    with col_analysis:
        st.subheader("🤖 Claude's Analysis")
        st.caption(f"Task: _{r['task']}_")
        st.markdown(r["analysis"])
        st.caption(f"Completed in {r['elapsed']}s")

# ── How It Works ──────────────────────────────────────────────────────────────
st.divider()
with st.expander("⚙️ How This Works", expanded=False):
    st.markdown("""
**Architecture:** Claude + Playwright running in a 4-step agentic loop.

1. **Navigate** — Playwright launches a headless Chromium browser and loads the target URL
2. **Capture** — Full-page screenshot (PNG) + `document.body.innerText` extraction
3. **Analyze** — Both are sent to Claude (vision + text). Claude reads the screenshot like a human would
4. **Respond** — Claude's structured analysis returned in the UI

**Why this matters for your use case:**
- The agent can handle any website — login flows, dynamic SPAs, paginated tables
- Claude's vision means it can read charts, images, and complex layouts, not just raw text
- Playwright supports multi-step workflows: click, fill forms, wait for network, download files
- The agent loop can be extended: retry on failure, follow links, aggregate across pages

**Production extensions:**
- Add authentication (session cookies, OAuth flows)
- Multi-step navigation (search → click result → extract data)
- Scheduled runs via cron / n8n
- Output to Airtable, Notion, Slack, or any API
    """)
