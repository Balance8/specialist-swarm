# StoryScript — the handoff contract

This is the shared interface for the **story video swarm**. The Story Architect agent
emits a `StoryScript`; the Visuals agent and the Coordinator consume it. Build against
this document.

## The three lanes

| Role | Owns | Reads | Writes |
| --- | --- | --- | --- |
| **Story Architect** (this repo's piece) | The narrative: what to say, why, and what to show | The raw input | `StoryScript` (below) |
| **Visuals agent** (teammate) | How it looks: concrete shapes, icons, layout, color, motion | `StoryScript` (`visual_intent`, `through_line_motif`, `tone`) | per-beat object specs |
| **Coordinator** (teammate) | The timeline: composing beats + objects into a Remotion render | `StoryScript` (`duration_s`, `transition_out`, `order`) + object specs | the final ≤20s video |

The boundary is deliberate. The Story Architect never names a font, color, or coordinate —
it describes **imagery and mood** (`visual_intent`) and leaves the rendering to the visuals
agent. This mirrors the swarm principle already in this repo: specialists own lanes, the
coordinator synthesizes.

## Schema

```json
{
  "title": "string — internal slug, not shown on screen",
  "logline": "string — [subject] wants [goal] but faces [pressure], revealing [stakes]",
  "theme": "string — dominant motif, e.g. 'fragmentation -> unity'",
  "tone": "string — e.g. 'punchy, builder-energy, optimistic'",
  "through_line_motif": "string — the ONE visual metaphor that transforms across all 4 beats",
  "total_duration_s": 20,
  "beats": [
    {
      "id": "problem | status_quo | missing_piece | bring_together",
      "order": 0,
      "duration_s": 4,
      "on_screen_text": ["primary line", "optional sub-line"],
      "emphasis_keywords": ["subset of words appearing in on_screen_text"],
      "narrative_note": "string — what the beat accomplishes; context for the visuals agent",
      "visual_intent": "string — render-agnostic imagery/mood/motion; how the motif looks here",
      "transition_out": "cut | morph | build | reveal"
    }
  ],
  "kicker": "string | null — optional final logo/CTA frame text"
}
```

## Invariants the consumers can rely on

- Exactly **4 beats**, ids `problem` → `status_quo` → `missing_piece` → `bring_together`, `order` 0..3.
- `sum(beats[].duration_s) <= total_duration_s` (default 20).
- `on_screen_text`: hook (`problem`) primary line ≤ 6 words; all other primary lines ≤ 8 words.
- `emphasis_keywords[i]` only contains words present in that beat's `on_screen_text`.
- `through_line_motif` describes a single metaphor whose state each beat's `visual_intent` references.
- The whole object is valid JSON. The agent emits exactly one fenced ```json block.

See `skills/narrative-arc/SKILL.md` for the full authoring spec (the single source of truth
the agent follows). `run_story_agent.py` validates a produced `StoryScript` against these
invariants and prints PASS/FAIL.
