#!/usr/bin/env python3
"""Parse navarch-build-log transcripts and generate a self-contained HTML review app."""

import argparse
import json
import os
import re
import webbrowser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRS = ["cursor", "claude"]


def parse_file(filepath: str, relpath: str) -> list[dict]:
    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    # Split on --- delimiters that separate sections
    sections = re.split(r"\n---\n", text)

    turns = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Check if this section starts with ## User or ## Assistant
        m = re.match(r"^## (User|Assistant)\s*\n(.*)", section, re.DOTALL)
        if m:
            role = m.group(1).lower()
            content = m.group(2).strip()
            # Skip empty turns
            if not content:
                continue
            turns.append(
                {
                    "file": relpath,
                    "turnIndex": len(turns),
                    "role": role,
                    "content": content,
                }
            )

    return turns


TOOL_USE_PATTERNS = [
    re.compile(r"^```"),                          # code fences (file contents, command output)
    re.compile(r"^\[Request interrupted"),         # framework interrupts
    re.compile(r"^<task-notification>"),            # task notifications
    re.compile(r"^<local-command-"),                # local command output
    re.compile(r"^<command-name>"),                 # slash command invocations
    re.compile(r"^<command-message>"),              # slash command messages
    re.compile(r"^<local-command-stdout>"),         # command stdout
    re.compile(r"^<local-command-caveat>"),         # command caveats
    re.compile(r"^This session is being continued from a previous conversation"),
]


def is_tool_use(content: str) -> bool:
    return any(p.match(content) for p in TOOL_USE_PATTERNS)


def collect_turns(
    roles: set[str] | None = None, skip_tool_use: bool = False
) -> list[dict]:
    all_turns = []
    for d in DIRS:
        dirpath = os.path.join(SCRIPT_DIR, d)
        if not os.path.isdir(dirpath):
            continue
        for fname in sorted(os.listdir(dirpath)):
            if not fname.endswith(".md"):
                continue
            filepath = os.path.join(dirpath, fname)
            relpath = os.path.join(d, fname)
            turns = parse_file(filepath, relpath)
            if roles:
                turns = [t for t in turns if t["role"] in roles]
            if skip_tool_use:
                turns = [t for t in turns if not is_tool_use(t["content"])]
            all_turns.extend(turns)

    return all_turns


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chat Review</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  :root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-dim: #8b949e;
    --user: #388bfd;
    --user-bg: #1a2332;
    --assistant: #8b949e;
    --assistant-bg: #1c1e24;
    --flag: #f85149;
    --flag-bg: #3d1214;
    --progress: #238636;
    --accent: #58a6ff;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* Top bar */
  .top-bar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
    min-height: 52px;
  }

  .filename {
    font-size: 13px;
    color: var(--accent);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 360px;
    flex-shrink: 0;
  }

  .counter {
    font-size: 14px;
    font-weight: 600;
    white-space: nowrap;
    flex-shrink: 0;
  }

  .progress-wrap {
    flex: 1;
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
    min-width: 80px;
  }

  .progress-fill {
    height: 100%;
    background: var(--progress);
    transition: width 0.2s;
    border-radius: 3px;
  }

  .flag-count {
    font-size: 13px;
    color: var(--flag);
    white-space: nowrap;
    flex-shrink: 0;
  }

  /* Main content area */
  .content {
    flex: 1;
    overflow-y: auto;
    padding: 24px 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  /* Previous turn (context) */
  .prev-turn {
    opacity: 0.45;
    font-size: 14px;
    max-height: 200px;
    overflow-y: auto;
    padding: 16px 20px;
    background: var(--surface);
    border-radius: 8px;
    border: 1px solid var(--border);
    flex-shrink: 0;
  }

  .prev-turn .badge {
    font-size: 11px;
    margin-bottom: 8px;
  }

  /* Current turn */
  .current-turn {
    flex: 1;
    overflow-y: auto;
    padding: 20px 24px;
    background: var(--surface);
    border-radius: 8px;
    border: 1px solid var(--border);
    font-size: 15px;
    line-height: 1.6;
    transition: border-color 0.15s;
  }

  .current-turn.flagged {
    border-left: 4px solid var(--flag);
    background: var(--flag-bg);
  }

  .current-turn.role-user { border-top: 2px solid var(--user); }
  .current-turn.role-assistant { border-top: 2px solid var(--assistant); }

  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 12px;
  }

  .badge-user { background: var(--user-bg); color: var(--user); }
  .badge-assistant { background: var(--assistant-bg); color: var(--assistant); }

  .flag-icon {
    float: right;
    font-size: 18px;
    cursor: pointer;
    user-select: none;
    opacity: 0.3;
    transition: opacity 0.15s;
  }

  .flag-icon:hover { opacity: 0.7; }
  .flag-icon.active { opacity: 1; color: var(--flag); }

  /* Markdown content */
  .md-body h1, .md-body h2, .md-body h3 { margin: 16px 0 8px; }
  .md-body p { margin: 8px 0; }
  .md-body ul, .md-body ol { margin: 8px 0 8px 24px; }
  .md-body li { margin: 2px 0; }

  .md-body pre {
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px 16px;
    overflow-x: auto;
    font-size: 13px;
    line-height: 1.45;
    margin: 8px 0;
  }

  .md-body code {
    font-family: "SF Mono", "Fira Code", "Fira Mono", Menlo, monospace;
    font-size: 0.9em;
  }

  .md-body :not(pre) > code {
    background: rgba(110, 118, 129, 0.2);
    padding: 2px 6px;
    border-radius: 4px;
  }

  .md-body blockquote {
    border-left: 3px solid var(--border);
    padding-left: 16px;
    color: var(--text-dim);
    margin: 8px 0;
  }

  .md-body table {
    border-collapse: collapse;
    margin: 8px 0;
    width: 100%;
  }

  .md-body th, .md-body td {
    border: 1px solid var(--border);
    padding: 6px 12px;
    text-align: left;
  }

  .md-body th { background: rgba(110, 118, 129, 0.1); }

  .md-body a { color: var(--accent); text-decoration: none; }
  .md-body a:hover { text-decoration: underline; }

  .md-body img { max-width: 100%; border-radius: 6px; }

  /* Bottom bar */
  .bottom-bar {
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 8px 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    flex-shrink: 0;
    flex-wrap: wrap;
  }

  .shortcut {
    font-size: 12px;
    color: var(--text-dim);
    white-space: nowrap;
  }

  .shortcut kbd {
    display: inline-block;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 1px 6px;
    font-family: monospace;
    font-size: 11px;
    color: var(--text);
    margin: 0 2px;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 8px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--text-dim); }
</style>
</head>
<body>

<div class="top-bar">
  <span class="filename" id="filename"></span>
  <span class="counter" id="counter"></span>
  <div class="progress-wrap"><div class="progress-fill" id="progress"></div></div>
  <span class="flag-count" id="flagCount"></span>
</div>

<div class="content">
  <div class="prev-turn" id="prevTurn"></div>
  <div class="current-turn" id="currentTurn"></div>
</div>

<div class="bottom-bar">
  <span class="shortcut"><kbd>&rarr;</kbd> <kbd>j</kbd> <kbd>Space</kbd> next</span>
  <span class="shortcut"><kbd>&larr;</kbd> <kbd>k</kbd> prev</span>
  <span class="shortcut"><kbd>f</kbd> flag</span>
  <span class="shortcut"><kbd>s</kbd> next file</span>
  <span class="shortcut"><kbd>S</kbd> prev file</span>
  <span class="shortcut"><kbd>g</kbd> next flagged</span>
  <span class="shortcut"><kbd>e</kbd> export</span>
</div>

<script>
const TURNS = __TURNS_JSON__;

let idx = 0;
let flags = new Set();

// Restore state from localStorage
const savedIdx = localStorage.getItem("review_idx");
const savedFlags = localStorage.getItem("review_flags");
if (savedIdx !== null) idx = Math.min(parseInt(savedIdx, 10), TURNS.length - 1);
if (savedFlags) {
  try { flags = new Set(JSON.parse(savedFlags)); } catch(e) {}
}

function saveState() {
  localStorage.setItem("review_idx", idx);
  localStorage.setItem("review_flags", JSON.stringify([...flags]));
}

function renderMarkdown(text) {
  try {
    return marked.parse(text, { breaks: true });
  } catch(e) {
    return "<pre>" + text.replace(/</g, "&lt;") + "</pre>";
  }
}

function render() {
  const turn = TURNS[idx];
  if (!turn) return;

  // Filename
  document.getElementById("filename").textContent = turn.file;

  // Counter
  document.getElementById("counter").textContent = `${idx + 1} / ${TURNS.length}`;

  // Progress
  document.getElementById("progress").style.width = `${((idx + 1) / TURNS.length) * 100}%`;

  // Flag count
  document.getElementById("flagCount").textContent = `\u2691 ${flags.size} flagged`;

  // Previous turn
  const prevEl = document.getElementById("prevTurn");
  if (idx > 0 && TURNS[idx - 1].file === turn.file) {
    const prev = TURNS[idx - 1];
    const badgeClass = prev.role === "user" ? "badge-user" : "badge-assistant";
    prevEl.innerHTML = `<div class="badge ${badgeClass}">${prev.role}</div><div class="md-body">${renderMarkdown(prev.content)}</div>`;
    prevEl.style.display = "block";
  } else {
    prevEl.style.display = "none";
  }

  // Current turn
  const curEl = document.getElementById("currentTurn");
  const badgeClass = turn.role === "user" ? "badge-user" : "badge-assistant";
  const flagKey = `${turn.file}::${turn.turnIndex}`;
  const isFlagged = flags.has(flagKey);

  curEl.className = "current-turn role-" + turn.role + (isFlagged ? " flagged" : "");
  curEl.innerHTML =
    `<span class="flag-icon ${isFlagged ? 'active' : ''}" onclick="toggleFlag()">\u2691</span>` +
    `<div class="badge ${badgeClass}">${turn.role}</div>` +
    `<div class="md-body">${renderMarkdown(turn.content)}</div>`;

  curEl.scrollTop = 0;
  saveState();
}

function toggleFlag() {
  const turn = TURNS[idx];
  const key = `${turn.file}::${turn.turnIndex}`;
  if (flags.has(key)) flags.delete(key);
  else flags.add(key);
  render();
}

function go(newIdx) {
  idx = Math.max(0, Math.min(TURNS.length - 1, newIdx));
  render();
}

function nextFile() {
  const curFile = TURNS[idx].file;
  for (let i = idx + 1; i < TURNS.length; i++) {
    if (TURNS[i].file !== curFile) { go(i); return; }
  }
}

function prevFile() {
  const curFile = TURNS[idx].file;
  // Find start of current file
  let start = idx;
  while (start > 0 && TURNS[start - 1].file === curFile) start--;
  if (start === 0) return;
  // Go to start of previous file
  const prevFileEnd = start - 1;
  const prevFileName = TURNS[prevFileEnd].file;
  let prevStart = prevFileEnd;
  while (prevStart > 0 && TURNS[prevStart - 1].file === prevFileName) prevStart--;
  go(prevStart);
}

function nextFlagged() {
  for (let i = idx + 1; i < TURNS.length; i++) {
    const t = TURNS[i];
    if (flags.has(`${t.file}::${t.turnIndex}`)) { go(i); return; }
  }
  // Wrap around
  for (let i = 0; i < idx; i++) {
    const t = TURNS[i];
    if (flags.has(`${t.file}::${t.turnIndex}`)) { go(i); return; }
  }
}

function exportFlagged() {
  const flagged = TURNS.filter(t => flags.has(`${t.file}::${t.turnIndex}`));
  const blob = new Blob([JSON.stringify(flagged, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "flagged_turns.json";
  a.click();
  URL.revokeObjectURL(url);
}

document.addEventListener("keydown", (e) => {
  // Don't capture if user is typing in an input
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

  switch(e.key) {
    case "ArrowRight": case "j": case " ": e.preventDefault(); go(idx + 1); break;
    case "ArrowLeft": case "k": e.preventDefault(); go(idx - 1); break;
    case "f": toggleFlag(); break;
    case "s": nextFile(); break;
    case "S": prevFile(); break;
    case "g": nextFlagged(); break;
    case "e": exportFlagged(); break;
  }
});

render();
</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Build chat review HTML")
    parser.add_argument(
        "--user-only",
        action="store_true",
        help="Only include user turns (implies --skip-tool-use)",
    )
    parser.add_argument(
        "--skip-tool-use",
        action="store_true",
        help="Filter out tool-use noise (code fences, task notifications, etc.)",
    )
    args = parser.parse_args()

    roles = {"user"} if args.user_only else None
    skip_tool_use = args.skip_tool_use or args.user_only
    turns = collect_turns(roles, skip_tool_use=skip_tool_use)
    print(f"Parsed {len(turns)} turns from {len(set(t['file'] for t in turns))} files")

    turns_json = json.dumps(turns, ensure_ascii=False)
    # Escape </script> so it doesn't break the embedding <script> tag
    turns_json = turns_json.replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__TURNS_JSON__", turns_json)

    out_path = os.path.join(SCRIPT_DIR, "review.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote {out_path}")
    webbrowser.open("file://" + out_path)


if __name__ == "__main__":
    main()
