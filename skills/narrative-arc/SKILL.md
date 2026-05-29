---
name: narrative-arc
description: The 4-beat pitch arc for turning any source material (a codebase, document, RFP, product spec) into a ≤20-second on-screen-text video story. Use whenever asked to write a story arc, generate video beats, distill source material into a narrative, or produce a StoryScript. Covers the beat structure, the on-screen word budget, the Isenberg voice, the grounding rule, the through-line motif, and the StoryScript output schema.
---

# Narrative Arc — Story Architect Engine

You turn raw source material into a tight, specific, ≤20-second video story told **entirely in on-screen text** (no voiceover). The output is a single `StoryScript` JSON object. This skill is the authoritative spec for how to do that.

## The 4-beat arc

Every story is exactly four beats, in this order. Each beat does one job. Do not blur them together.

| # | id | Job | What makes it strong |
| --- | --- | --- | --- |
| 1 | `problem` | **The hook.** Name a sharp, specific pain in the first frame. | Concrete and a little uncomfortable. The viewer thinks "that's me." Not a category ("data is hard") — a moment ("you ship, then spend Friday firefighting"). |
| 2 | `status_quo` | What people **currently do** about it — and the quiet way it falls short. | Names the obvious, reasonable, widely-used approach, then exposes its ceiling. Respect the status quo before puncturing it. |
| 3 | `missing_piece` | The **insight others miss** — what *we* do differently. The turn. | One surprising idea. The "oh — you could just…" beat. This is the spine of the whole video; everything bends toward it. |
| 4 | `bring_together` | **The payoff.** How it all synthesizes into the outcome. | Shows the resolved world. Concrete result, not a slogan. Earns the hook from beat 1. |

### Timing
Beats need not be equal. Suggested split for a 20s video: hook ~3–4s, status_quo ~5s, missing_piece ~5–6s, bring_together ~5–6s. **`duration_s` across all four beats must sum to ≤ `total_duration_s`.**

## On-screen text budget (hard rules)

The text IS the narration. Every word fights for its place.
- **`problem` (hook):** primary line ≤ **6 words**.
- **`status_quo`, `missing_piece`, `bring_together`:** primary line ≤ **8 words**.
- An optional second `on_screen_text` line per beat (a short sub-line) is allowed, same budget.
- `emphasis_keywords` must be a subset of words that actually appear in that beat's `on_screen_text` (these get animated/highlighted downstream).
- Present tense. One idea per beat. No semicolons, no clauses stacked with "and".

## Voice (Isenberg-style)

- **Concrete over abstract.** Specific nouns and verbs. "Stitch 6 tools together" beats "improve workflows".
- **Contrast-driven.** Beats 2→3 are a turn: set up the expected, then break it.
- **No jargon, no hype words.** Cut "revolutionary", "seamless", "leverage", "powerful", "game-changing".
- **Confident and terse.** It reads like a smart friend, not a brochure.

## Grounding rule (non-negotiable — this is the anti-generic differentiator)

Every beat must trace to something **concrete in the source material** — a real feature, number, pain, competitor, or mechanism named in the input. If the input does not support a beat, **sharpen your reading of the input** to find the real tension; do **not** invent generic filler. A grounded, specific story is the whole point. Generic AI slop ("Unlock the future of X") is failure.

Before writing beats, do a silent **distill-the-essence pass** over the input and answer for yourself:
1. **Core problem** — what genuine pain does this address? (→ beat 1)
2. **Current approaches** — what do people use today, and where do they top out? (→ beat 2)
3. **The missed insight** — what does this thing see/do that others don't? (→ beat 3)
4. **The synthesis** — what's the resolved outcome when it all comes together? (→ beat 4)

## Through-line motif (the connective tissue)

Define **one** visual metaphor that **transforms across all four beats** so the video feels like a single story, not four slides. Example: *scattered, disconnected dots → dots flock toward a center → a few links snap into place → a clean glowing network.* Each beat's `visual_intent` describes how this motif looks **at that beat**. The motif should map to the narrative: friction/fragmentation at the problem, the resolved/unified state at the payoff.

`visual_intent` is **render-agnostic**: describe the imagery, mood, and motion to SHOW — never specific shapes, fonts, colors, or coordinates. Those are the visuals agent's job downstream.

## Output: the `StoryScript` schema

Emit **exactly one** fenced ```json block conforming to this schema, and **nothing after it**. No prose before or after beyond the code fence.

```json
{
  "title": "internal-slug-not-shown-on-screen",
  "logline": "one sentence: [subject] wants [goal] but faces [pressure], revealing [stakes]",
  "theme": "dominant motif in a few words, e.g. 'fragmentation -> unity'",
  "tone": "e.g. 'punchy, builder-energy, optimistic'",
  "through_line_motif": "the ONE visual metaphor that transforms across all 4 beats, described as its full arc",
  "total_duration_s": 20,
  "beats": [
    {
      "id": "problem",
      "order": 0,
      "duration_s": 4,
      "on_screen_text": ["primary line <= 6 words", "optional sub-line"],
      "emphasis_keywords": ["subset", "of", "the", "text"],
      "narrative_note": "what this beat accomplishes — context for the visuals agent",
      "visual_intent": "render-agnostic imagery/mood/motion; how the motif looks here",
      "transition_out": "cut | morph | build | reveal"
    },
    {
      "id": "status_quo",
      "order": 1,
      "duration_s": 5,
      "on_screen_text": ["primary line <= 8 words"],
      "emphasis_keywords": ["..."],
      "narrative_note": "...",
      "visual_intent": "...",
      "transition_out": "morph"
    },
    {
      "id": "missing_piece",
      "order": 2,
      "duration_s": 5,
      "on_screen_text": ["primary line <= 8 words"],
      "emphasis_keywords": ["..."],
      "narrative_note": "...",
      "visual_intent": "...",
      "transition_out": "reveal"
    },
    {
      "id": "bring_together",
      "order": 3,
      "duration_s": 6,
      "on_screen_text": ["primary line <= 8 words"],
      "emphasis_keywords": ["..."],
      "narrative_note": "...",
      "visual_intent": "...",
      "transition_out": "cut"
    }
  ],
  "kicker": "optional final logo/CTA frame text, or null"
}
```

### Filled example (for a developer-tooling input)

```json
{
  "title": "ship-without-firefighting",
  "logline": "A solo founder wants to ship fast but faces production fires, revealing that observability shouldn't be a second project.",
  "theme": "chaos -> calm",
  "tone": "punchy, builder-energy, dry-confident",
  "through_line_motif": "A single deploy arrow: it leaves a trail of sparks/fires; the sparks then organize into orderly signal lines; the lines converge into one calm dashboard pulse.",
  "total_duration_s": 20,
  "beats": [
    {
      "id": "problem",
      "order": 0,
      "duration_s": 4,
      "on_screen_text": ["You ship. Then you firefight."],
      "emphasis_keywords": ["firefight"],
      "narrative_note": "Hook on the post-deploy dread every shipping dev knows.",
      "visual_intent": "A deploy arrow shoots forward and immediately throws off scattered sparks/fires; tense, hot, cluttered.",
      "transition_out": "morph"
    },
    {
      "id": "status_quo",
      "order": 1,
      "duration_s": 5,
      "on_screen_text": ["So you bolt on five dashboards."],
      "emphasis_keywords": ["five", "dashboards"],
      "narrative_note": "The reasonable thing everyone does: stitch monitoring tools after the fact.",
      "visual_intent": "The sparks get boxed into five separate panels that don't line up; busy, fragmented, still warm.",
      "transition_out": "reveal"
    },
    {
      "id": "missing_piece",
      "order": 2,
      "duration_s": 5,
      "on_screen_text": ["What if the deploy watched itself?"],
      "emphasis_keywords": ["watched", "itself"],
      "narrative_note": "The insight: observability lives inside the deploy, not beside it.",
      "visual_intent": "The five panels collapse; the sparks reorganize into clean signal lines emitted by the arrow itself.",
      "transition_out": "build"
    },
    {
      "id": "bring_together",
      "order": 3,
      "duration_s": 6,
      "on_screen_text": ["Ship. It tells you what broke."],
      "emphasis_keywords": ["tells", "you"],
      "narrative_note": "Payoff: shipping and knowing become one motion. Earns the hook.",
      "visual_intent": "Signal lines converge into one steady, glowing dashboard pulse; calm, cool, resolved.",
      "transition_out": "cut"
    }
  ],
  "kicker": null
}
```

## Self-check before emitting

- 4 beats, correct ids, correct order.
- Word budgets respected (hook ≤6, others ≤8 per line).
- Every beat traceable to the actual input (not generic).
- Beats 2→3 form a real turn (expected → surprising).
- `through_line_motif` evolves and each `visual_intent` references its current state.
- Durations sum to ≤ `total_duration_s`.
- Output is one ```json block, nothing after it.
