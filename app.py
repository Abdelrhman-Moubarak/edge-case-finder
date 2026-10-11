"""Edge Case Finder: Streamlit frontend.

Run with: streamlit run app.py
Needs a recent Streamlit (tested on 1.65): pip install -U streamlit python-dotenv
Set DEBUG_REFERENCE=1 in .env to show and print the reference function.
"""

import html
import json
import math
import os
import time

from dotenv import load_dotenv
import streamlit as st
from streamlit.components.v2 import component as create_component

load_dotenv()

st.set_page_config(page_title="Edge Case Finder", page_icon="🌿", layout="wide")

DEBUG = os.getenv("DEBUG_REFERENCE") == "1"

# ---------------------------------------------------------------- styling
PAPER = "#F6F1E7"
INK = "#1F3A2E"
AMBER = "#C98A1B"
MUTED = "#6B7568"
LINE = "#E1D9C6"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

html, body, .stApp, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {INK}; }}
.stApp {{ background: {PAPER}; }}
header[data-testid="stHeader"], #MainMenu, footer {{ display: none; }}
.block-container {{ max-width: 1180px; padding: 4.5rem 3rem 7rem 3rem; }}

.hero {{ text-align: center; margin-bottom: 3.5rem; }}
.eyebrow {{ font-size: 0.72rem; letter-spacing: 0.16em; text-transform: uppercase; color: {MUTED}; font-weight: 600; }}
.title {{ font-family: 'Fraunces', serif; font-size: 3.4rem; line-height: 1.1; margin: 0.7rem 0 0.9rem 0; color: {INK}; }}
.tagline {{ color: {MUTED}; font-size: 1.05rem; line-height: 1.6; max-width: 36rem; margin: 0 auto; }}
.rule {{ width: 3.5rem; height: 3px; background: {AMBER}; margin: 1.8rem auto 0 auto; border: 0; }}
.label {{ font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase; color: {MUTED}; font-weight: 600; margin: 0 0 0.5rem 0; }}

.stTextArea textarea {{ background: #FBF8F1; border: 1px solid {LINE}; border-radius: 10px; color: {INK}; min-height: 280px !important; max-height: 560px; font-family: 'SFMono-Regular', Consolas, monospace; font-size: 0.88rem; }}
.stTextArea textarea:focus {{ border-color: {INK}; box-shadow: none; }}

div.stButton > button {{ border-radius: 10px; padding: 0.65rem 1.4rem; font-weight: 600; border: 1px solid {INK}; background: transparent; color: {INK}; }}
div.stButton > button[kind="primary"] {{ background: {INK}; color: {PAPER}; }}
div.stButton > button:hover {{ border-color: {AMBER}; color: {AMBER}; }}
div.stButton > button[kind="primary"]:hover {{ background: {INK}; color: {PAPER}; border-color: {AMBER}; }}
div.stButton > button:disabled {{ opacity: 0.45; }}
div.stDownloadButton > button {{ border-radius: 10px; padding: 0.65rem 1.4rem; font-weight: 600; border: 1px solid {INK}; background: transparent; color: {INK}; }}
div.stDownloadButton > button:hover {{ border-color: {AMBER}; color: {AMBER}; }}

.section-title {{ font-family: 'Fraunces', serif; font-size: 1.7rem; margin: 0 0 0.3rem 0; }}
.section-sub {{ color: {MUTED}; font-size: 0.92rem; margin-bottom: 1.6rem; }}

.case {{ padding: 1.3rem 0; border-top: 1px solid {LINE}; }}
.case.last {{ border-bottom: 1px solid {LINE}; }}
.case-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; flex-wrap: wrap; }}
.case-name {{ font-weight: 600; font-size: 1rem; }}
.case-num {{ color: {MUTED}; font-weight: 500; font-variant-numeric: tabular-nums; margin-right: 0.7rem; }}
.case-call {{ font-family: 'SFMono-Regular', Consolas, monospace; font-size: 0.85rem; background: #EFE8D6; padding: 0.15rem 0.5rem; border-radius: 6px; display: inline-block; margin: 0.5rem 0; word-break: break-all; }}
.case-reason {{ color: {MUTED}; font-size: 0.92rem; line-height: 1.55; }}
.tag {{ font-size: 0.78rem; font-weight: 600; padding: 0.2rem 0.7rem; border-radius: 999px; white-space: nowrap; }}
.tag-returns {{ background: {INK}; color: {PAPER}; }}
.tag-raises {{ background: transparent; color: {AMBER}; border: 1px solid {AMBER}; }}

.failed {{ border-left: 3px solid {AMBER}; padding: 0.2rem 0 0.2rem 1rem; margin-bottom: 1.1rem; }}
.stAlert {{ border-radius: 10px; }}
[data-testid="stExpander"] {{ border: 1px solid {LINE}; border-radius: 10px; background: transparent; }}
</style>
""",
    unsafe_allow_html=True,
)

# Runs in the page itself (no iframe): swaps the tab icon while generating
# and scrolls down to the results area when a run starts.
_TAB_EFFECTS_JS = """
export default function (component) {
  const { data, parentElement } = component

  let link = document.querySelector("link[rel~='icon']")
  if (!link) {
    link = document.createElement("link")
    link.rel = "icon"
    document.head.appendChild(link)
  }
  if (!window.__ecfOriginalIcon) window.__ecfOriginalIcon = link.href

  const svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>" +
    "<rect width='64' height='64' rx='14' fill='#1F3A2E'/>" +
    "<path d='M24 18 L48 32 L24 46 Z' fill='#F6F1E7'/></svg>"

  if (data.running) {
    link.href = "data:image/svg+xml," + encodeURIComponent(svg)
  } else {
    link.href = window.__ecfOriginalIcon
  }

  if (data.running && !window.__ecfWasRunning) {
    const host = parentElement.getRootNode().host || parentElement
    setTimeout(() => host.scrollIntoView({ behavior: "smooth", block: "start" }), 150)
  }
  window.__ecfWasRunning = data.running
}
"""

_TAB_EFFECTS = create_component(
    "ecf_tab_effects", html="<div></div>", js=_TAB_EFFECTS_JS
)

# ---------------------------------------------------------------- backend
missing = [k for k in ("NGROK_URL", "API_KEY") if not os.getenv(k)]
if missing:
    st.error(
        f"Missing {', '.join(missing)}. Add them to a .env file next to app.py, "
        "then restart the app."
    )
    st.stop()

try:
    from langchain_core.exceptions import OutputParserException
    from src.chains import generate_edge_cases
    from src.runner import RunnerError
except RuntimeError as exc:
    st.error(f"Could not start the backend: {exc}")
    st.stop()

# ---------------------------------------------------------------- state
ss = st.session_state
ss.setdefault("running", False)
ss.setdefault("pending", None)
ss.setdefault("result", None)
ss.setdefault("error", None)
ss.setdefault("code", "")
ss.setdefault("desc", "")


def format_duration(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m {secs:02d}s"


def describe(case: dict) -> tuple[str, str]:
    if case.get("expected_exception"):
        return f"raises {case['expected_exception']}", "raises"
    return f"returns {case.get('expected')}", "returns"


def render_cases(cases: list[dict], start: int, last_index: int) -> str:
    cards = []
    for offset, c in enumerate(cases):
        number = start + offset
        outcome, kind = describe(c)
        last = " last" if number == last_index else ""
        cards.append(
            f'<div class="case{last}">'
            '<div class="case-head">'
            f'<span class="case-name"><span class="case-num">{number:02d}</span>{html.escape(c["name"])}</span>'
            f'<span class="tag tag-{kind}">{html.escape(outcome)}</span>'
            "</div>"
            f'<div class="case-call">{html.escape(c["call"])}</div>'
            f'<div class="case-reason">{html.escape(c["reason"])}</div>'
            "</div>"
        )
    return "".join(cards)


def to_markdown(result: dict) -> str:
    lines = ["# Edge cases", ""]
    for i, c in enumerate(result["cases"], start=1):
        outcome, _ = describe(c)
        lines += [f"## {i}. {c['name']}", f"- Call: `{c['call']}`", f"- Outcome: {outcome}", f"- Why: {c['reason']}", ""]
    if result["failed"]:
        lines += ["# Dropped cases", ""]
        for f in result["failed"]:
            lines.append(f"- `{f['call']}`: {f['reason']}")
        lines.append("")
    return "\n".join(lines)


def to_json(result: dict) -> str:
    return json.dumps({"cases": result["cases"], "failed": result["failed"]}, indent=2)


def clear_all() -> None:
    ss.result = None
    ss.error = None
    ss.code = ""
    ss.desc = ""


# ---------------------------------------------------------------- header
st.markdown(
    '<div class="hero">'
    '<div class="eyebrow">Test ideas from intent</div>'
    '<div class="title">Edge Case Finder</div>'
    '<div class="tagline">Expected values come from your description, '
    "not from your code, so a bug in the function cannot hide itself.</div>"
    '<hr class="rule">'
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- inputs
col_code, col_desc = st.columns(2, gap="large")

with col_code:
    st.markdown('<div class="label">Your function</div>', unsafe_allow_html=True)
    st.text_area(
        "Function code",
        key="code",
        height="content",
        placeholder="def calculate_shipping_cost(weight, distance, express):\n    ...",
        label_visibility="collapsed",
        disabled=ss.running,
    )

with col_desc:
    st.markdown('<div class="label">What it should do</div>', unsafe_allow_html=True)
    st.text_area(
        "Description",
        key="desc",
        height="content",
        placeholder="Plain English. Include limits, rules and what should be rejected.",
        label_visibility="collapsed",
        disabled=ss.running,
    )

st.write("")
with st.container(horizontal=True, horizontal_alignment="right"):
    st.button("Clear", on_click=clear_all, disabled=ss.running)
    run_clicked = st.button("Generate edge cases", type="primary", disabled=ss.running)

if run_clicked:
    if not ss.code.strip() or not ss.desc.strip():
        st.warning("Please fill in both the function and its description.")
    else:
        ss.pending = (ss.code, ss.desc)
        ss.running = True
        ss.error = None
        st.rerun()

# ---------------------------------------------------------------- results
_TAB_EFFECTS(data={"running": ss.running}, key="tab_effects")

if ss.running and ss.pending:
    st.write("")
    code, desc = ss.pending
    try:
        started = time.time()

        def on_step(message: str) -> None:
            st.write(message)

        with st.status("Working on it. Keep this tab open.", expanded=True) as status:
            suite, reference_code, failed_cases = generate_edge_cases(
                code, desc, on_step=on_step
            )
            seconds = time.time() - started
            status.update(
                label=f"Done in {format_duration(seconds)}",
                state="complete",
                expanded=False,
            )
        ss.result = {
            "cases": [c.model_dump() for c in suite.cases],
            "reference": reference_code,
            "failed": failed_cases,
            "seconds": seconds,
        }
        if DEBUG:
            print("\n--- reference function ---\n" + reference_code + "\n--------------------------", flush=True)
    except RuntimeError as exc:
        ss.error = (
            "Could not reach the model server. Check that it is running and that "
            f"NGROK_URL and API_KEY are correct.\n\nDetails: {exc}"
        )
    except OutputParserException:
        ss.error = "The model returned malformed output. Try again, or simplify the description."
    except RunnerError as exc:
        ss.error = f"No reference function could be produced from the description.\n\nDetails: {exc}"
    except ValueError as exc:
        ss.error = f"Something is wrong with the input: {exc}"
    finally:
        ss.running = False
        ss.pending = None
    st.rerun()

elif ss.error:
    st.write("")
    st.error(ss.error)

elif ss.result:
    res = ss.result
    cases = res["cases"]
    n = len(cases)
    half = math.ceil(n / 2)

    st.write("")
    st.markdown(f'<div class="section-title">{n} edge case{"s" if n != 1 else ""}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-sub">Generated in {format_duration(res["seconds"])}. '
        "Expected outcomes were derived from your description.</div>",
        unsafe_allow_html=True,
    )

    left_cases, right_cases = st.columns(2, gap="large")
    with left_cases:
        st.markdown(render_cases(cases[:half], 1, half), unsafe_allow_html=True)
    with right_cases:
        st.markdown(render_cases(cases[half:], half + 1, n), unsafe_allow_html=True)

    if DEBUG:
        st.write("")
        with st.expander("Reference function (debug)"):
            st.code(res["reference"], language="python")

    if res["failed"]:
        st.write("")
        st.markdown('<div class="section-title">Dropped cases</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-sub">These could not be verified, so they were left out.</div>',
            unsafe_allow_html=True,
        )
        for f in res["failed"]:
            st.markdown(
                '<div class="failed">'
                f'<div class="case-call">{html.escape(str(f.get("call", "")))}</div>'
                f'<div class="case-reason">{html.escape(str(f.get("reason", "")))}</div>'
                "</div>",
                unsafe_allow_html=True,
            )

    st.write("")
    with st.container(horizontal=True, horizontal_alignment="right"):
        st.download_button("Download .md", to_markdown(res), "edge_cases.md", "text/markdown")
        st.download_button("Download .json", to_json(res), "edge_cases.json", "application/json")