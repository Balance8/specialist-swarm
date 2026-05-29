"""
Stretch: add a Story Editor critic that gates story quality before visuals are built.

Mirrors stretch_critic_subagent.py. Creates a Story Editor agent and promotes the
Story Architect into a coordinator whose roster is the editor, then appends a
review-loop instruction to the architect's system prompt. The architect must run
its draft StoryScript past the editor before emitting the final JSON.

The editor scores the draft against a rubric (hook strength, grounding/specificity,
beat distinctness, word budget, motif continuity) and returns one verdict:
- SHIP    — solid; at most cosmetic notes
- REVISE  — specific fixes (≤5); architect addresses them and resubmits
- RESHAPE — the arc itself is wrong; architect rethinks beats once

Saves .story_editor_id.

Usage:
    python create_story_editor.py
"""

import os
from pathlib import Path

from anthropic import Anthropic


EDITOR_SYSTEM = """\
You are the Story Editor. You don't write stories — you review them, hard, before
they go to the visuals team. You receive a draft StoryScript JSON and the original
source material.

Score the draft against this rubric:
1. HOOK — does beat 1 land a specific, uncomfortable pain in the first frame? A
   generic category ("data is hard") fails; a concrete moment passes.
2. GROUNDING — does every beat trace to something real in the source (a feature,
   number, mechanism)? Generic AI filler fails.
3. TURN — do beats 2 -> 3 form a real surprise (expected approach -> missed insight)?
4. WORD BUDGET — hook primary line ≤ 6 words; other primary lines ≤ 8 words.
5. MOTIF CONTINUITY — does through_line_motif actually evolve, and does each beat's
   visual_intent reference its current state?

Deliver exactly one verdict, led by the verdict word:

- VERDICT: SHIP — the story is strong; list at most cosmetic suggestions.
- VERDICT: REVISE — list the specific fixes, terse, numbered, no more than 5. If you
  need more than 5, the arc isn't ready — use RESHAPE instead.
- VERDICT: RESHAPE — the beat structure or core insight is wrong. Say what the real
  story should be in two sentences.

Be sceptical. Your value is pushing back. A story that never gets edited ships slop.
"""


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    if not Path(".story_agent_id").exists():
        raise SystemExit("Missing .story_agent_id. Run create_story_agent.py first.")
    story_agent_id = Path(".story_agent_id").read_text().strip()

    client = Anthropic(
        default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
    )

    # Create the editor
    editor = client.beta.agents.create(
        name="Story Editor",
        model="claude-opus-4-7",  # the critic needs to be sharp
        system=EDITOR_SYSTEM,
        tools=[{"type": "agent_toolset_20260401"}],
        metadata={
            "hackathon": "partner-basecamp-2026",
            "track": "story-video-swarm",
            "role": "story_editor",
        },
    )
    Path(".story_editor_id").write_text(editor.id)
    print(f"Story Editor created: {editor.id}")

    # Promote the Story Architect to a coordinator with the editor in its roster,
    # and append the review-loop guidance to its system prompt.
    architect = client.beta.agents.retrieve(story_agent_id)
    new_system = architect.system + (
        "\n\n# Editor review (required before final output)\n\n"
        "Before emitting the final StoryScript JSON, send your DRAFT StoryScript "
        "(plus the source) to the Story Editor. It replies with SHIP, REVISE, or "
        "RESHAPE.\n"
        "- SHIP: emit the final StoryScript JSON.\n"
        "- REVISE: address every listed fix, then resubmit to the Editor. Repeat at "
        "most twice.\n"
        "- RESHAPE: rebuild the beats around the Editor's suggested story, then "
        "resubmit once.\n"
        "Only the final, editor-approved StoryScript is your output. Still emit it "
        "as exactly one ```json block with nothing after it.\n"
    )

    client.beta.agents.update(
        story_agent_id,
        version=architect.version,
        system=new_system,
        multiagent={
            "type": "coordinator",
            "agents": [{"type": "agent", "id": editor.id}],
        },
    )

    print("Story Architect promoted to coordinator; Story Editor added to its roster.")
    print("Re-run run_story_agent.py to see the editor gate the draft.")


if __name__ == "__main__":
    main()
