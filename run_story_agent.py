"""
Run the Story Architect alone against an inlined input and validate its output.

This is the solo smoke-test harness: iterate on the story agent without waiting
for the visuals agent or coordinator. It inlines a source file into the message,
streams the agent's events, extracts the StoryScript JSON, validates it against
the contract (story_contract.md), and saves it to outputs/storyscript.json.

Usage:
    python run_story_agent.py                                  # default sample
    python run_story_agent.py synthetic-data/rfp-acme-corp.md  # any input file
"""

import json
import os
import re
import sys
from pathlib import Path

from anthropic import Anthropic


DEFAULT_INPUT = Path("synthetic-data/sample-codebase-brief.md")
OUTPUT_DIR = Path("outputs")

VALID_BEAT_IDS = ["problem", "status_quo", "missing_piece", "bring_together"]
HOOK_WORD_LIMIT = 6
LINE_WORD_LIMIT = 8


def extract_storyscript(text: str) -> dict:
    """Pull the single fenced ```json block out of the agent's final message."""
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    blob = match.group(1) if match else text[text.find("{") : text.rfind("}") + 1]
    return json.loads(blob)


def _words(line: str) -> int:
    return len(line.split())


def validate(script: dict) -> list[tuple[str, bool, str]]:
    """Return a list of (rule, passed, detail). Mirrors story_contract.md invariants."""
    checks: list[tuple[str, bool, str]] = []

    for key in ("title", "logline", "theme", "tone", "through_line_motif", "beats"):
        checks.append((f"has `{key}`", key in script, ""))

    beats = script.get("beats", [])
    checks.append(("exactly 4 beats", len(beats) == 4, f"got {len(beats)}"))

    ids = [b.get("id") for b in beats]
    checks.append(("beat ids + order correct", ids == VALID_BEAT_IDS, f"got {ids}"))

    total = script.get("total_duration_s", 20)
    dur_sum = sum(b.get("duration_s", 0) for b in beats)
    checks.append((f"durations sum ≤ {total}s", dur_sum <= total, f"sum={dur_sum}"))

    motif = (script.get("through_line_motif") or "").strip()
    checks.append(("through_line_motif present", len(motif) > 10, ""))

    for b in beats:
        bid = b.get("id", "?")
        lines = b.get("on_screen_text", [])
        if not lines:
            checks.append((f"[{bid}] has on_screen_text", False, "empty"))
            continue
        limit = HOOK_WORD_LIMIT if bid == "problem" else LINE_WORD_LIMIT
        primary = lines[0]
        ok = _words(primary) <= limit
        checks.append((f"[{bid}] primary ≤ {limit} words", ok, f'"{primary}" ({_words(primary)}w)'))

        # emphasis_keywords must appear in the beat's text
        text_words = {w.strip(".,!?:;").lower() for line in lines for w in line.split()}
        kws = b.get("emphasis_keywords", [])
        stray = [k for k in kws if k.strip(".,!?:;").lower() not in text_words]
        checks.append((f"[{bid}] emphasis ⊆ text", not stray, f"stray={stray}" if stray else ""))

    return checks


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    if not Path(".story_agent_id").exists():
        raise SystemExit("Missing .story_agent_id. Run create_story_agent.py first.")
    if not Path(".environment_id").exists():
        raise SystemExit("Missing .environment_id. Run setup_environment.py first.")

    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    agent_id = Path(".story_agent_id").read_text().strip()
    environment_id = Path(".environment_id").read_text().strip()
    client = Anthropic()

    print(f"Input: {input_path}")
    source = input_path.read_text()

    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=environment_id,
        title=f"Story — {input_path.name}",
    )
    Path(".last_session_id").write_text(session.id)

    user_message = (
        "Turn the following source material into a ≤20-second video story. "
        "Follow your narrative-arc skill exactly and emit a single StoryScript "
        "JSON block as your final message — nothing after it.\n\n"
        f"=====  SOURCE: {input_path.name}  =====\n{source}"
    )

    print(f"\nStarting session against Story Architect {agent_id}...\n")
    print("=== EVENT STREAM ===\n")
    final_text_parts: list[str] = []

    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_message}]}],
        )
        for event in stream:
            t = event.type
            if t == "agent.tool_use":
                print(f"\n  [tool: {getattr(event, 'name', '?')}]", flush=True)
            elif t == "agent.message":
                for block in event.content:
                    if getattr(block, "type", None) == "text":
                        final_text_parts.append(block.text)
                        print(block.text, end="", flush=True)
            elif t == "session.status_idle":
                print("\n\n[story agent finished]")
                break

    final_text = "".join(final_text_parts)

    # Parse + validate
    print("\n=== VALIDATION ===")
    try:
        script = extract_storyscript(final_text)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"  FAILED to parse StoryScript JSON: {e}")
        raise SystemExit(1)

    checks = validate(script)
    passed = 0
    for rule, ok, detail in checks:
        mark = "PASS" if ok else "FAIL"
        suffix = f"  ({detail})" if detail else ""
        print(f"  [{mark}] {rule}{suffix}")
        passed += ok
    print(f"\n  {passed}/{len(checks)} checks passed")

    # Readable beat summary
    print("\n=== STORY ===")
    print(f"  logline: {script.get('logline')}")
    print(f"  motif:   {script.get('through_line_motif')}")
    for b in script.get("beats", []):
        text = " / ".join(b.get("on_screen_text", []))
        print(f"  [{b.get('id'):14s} {b.get('duration_s')}s] {text}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / "storyscript.json"
    out_path.write_text(json.dumps(script, indent=2))
    print(f"\nSaved StoryScript to {out_path}")
    print(f"View the session: https://platform.claude.com/sessions/{session.id}")


if __name__ == "__main__":
    main()
