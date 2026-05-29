"""
Create the Story Architect specialist and attach the narrative-arc skill.

This is the story-writing agent in the story-video swarm. It takes any inlined
input (a codebase brief, a document, an RFP) and emits a single StoryScript JSON
object — a ≤20-second, 4-beat, on-screen-text video story (see story_contract.md).

Combines the patterns from create_specialists.py (agent create) and
upload_skills.py (idempotent skill upload + attach by display_title). Safe to
re-run: an existing skill is reused, and re-attaching is a no-op.

Saves:
- .story_agent_id  (the agent)
- .story_skill_id  (the uploaded narrative-arc skill)

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python create_story_agent.py
"""

import os
from pathlib import Path

from anthropic import Anthropic
from anthropic.lib import files_from_dir


SKILL_DIR = Path("skills/narrative-arc")
SKILL_DISPLAY_TITLE = "Narrative Arc"


STORY_SYSTEM = """\
You are the Story Architect in a story-video swarm. You take a single piece of
source material — it might be a codebase, a product brief, a document, or an RFP —
and turn it into a ≤20-second video story told entirely in ON-SCREEN TEXT (no
voiceover). Your only deliverable is one StoryScript JSON object.

# Your process

1. DISTILL THE ESSENCE. Read the input closely and silently answer four questions:
   - Core problem: what genuine, specific pain does this address?
   - Current approaches: what do people do today, and where does it top out?
   - The missed insight: what does this thing see or do that others don't?
   - The synthesis: what's the resolved outcome when it all comes together?

2. MAP TO THE 4 BEATS — problem, status_quo, missing_piece, bring_together.

3. COMPRESS each beat to on-screen text within the word budget.

4. DEFINE the through-line motif and each beat's render-agnostic visual_intent.

5. EMIT the StoryScript as exactly one fenced ```json block, nothing after it.

# Rules that matter most

- GROUNDING: every beat must trace to something concrete in the input — a real
  feature, number, pain, or mechanism. If the input can't support a beat, sharpen
  your reading of the input. Never fall back to generic filler ("unlock the future
  of X"). A specific, grounded story is the entire point.
- STAY IN YOUR LANE: describe imagery and mood (visual_intent), never fonts,
  colors, or coordinates — those belong to the downstream visuals agent.

The attached `narrative-arc` skill is your authoritative spec: it defines the beat
structure, the word budget, the voice, the through-line motif, and the exact
StoryScript schema. Follow it precisely.
"""


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    if not (SKILL_DIR / "SKILL.md").exists():
        raise SystemExit(f"Missing {SKILL_DIR}/SKILL.md")

    client = Anthropic(
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    # 1. Upload the narrative-arc skill (or reuse an existing one by title).
    # Skills API enforces a unique display_title, so reuse is essential for
    # idempotent re-runs during the dev loop.
    print("Checking for existing narrative-arc skill...")
    existing_by_title: dict[str, str] = {}
    for page in client.beta.skills.list(source="custom"):
        existing_by_title[page.display_title] = page.id

    if SKILL_DISPLAY_TITLE in existing_by_title:
        skill_id = existing_by_title[SKILL_DISPLAY_TITLE]
        print(f"Reusing existing skill: {SKILL_DISPLAY_TITLE} ({skill_id})")
    else:
        print(f"Uploading skill: {SKILL_DISPLAY_TITLE}...")
        skill = client.beta.skills.create(
            display_title=SKILL_DISPLAY_TITLE,
            files=files_from_dir(str(SKILL_DIR)),
        )
        skill_id = skill.id
        print(f"  -> {skill_id}")

    Path(".story_skill_id").write_text(skill_id)

    # 2. Create the Story Architect with the skill attached.
    # Opus: narrative compression (any input -> a tight, grounded 4-beat story)
    # is the hardest, highest-leverage reasoning in this pipeline.
    print("Creating Story Architect agent...")
    agent = client.beta.agents.create(
        name="Story Architect",
        model="claude-opus-4-7",
        system=STORY_SYSTEM,
        tools=[{"type": "agent_toolset_20260401"}],
        skills=[{"type": "custom", "skill_id": skill_id, "version": "latest"}],
        metadata={
            "hackathon": "partner-basecamp-2026",
            "track": "story-video-swarm",
            "role": "story_architect",
        },
    )

    Path(".story_agent_id").write_text(agent.id)
    print(f"Story Architect created: {agent.id}")
    print(f"narrative-arc skill attached: {skill_id}")
    print("\nNext: python setup_environment.py (if needed), then python run_story_agent.py")


if __name__ == "__main__":
    main()
