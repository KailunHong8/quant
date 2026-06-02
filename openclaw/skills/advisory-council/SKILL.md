---
name: advisory-council
description: >
  Business advisory council that analyzes your knowledge base signals through
  parallel independent expert personas. Currently configured for 小红书 (RedNote)
  account growth analysis. Each expert sees only their relevant data slice.
  Output is a numbered digest of ranked recommendations.
version: 1.0.0
author: klaw
permissions:
  - filesystem:read
  - exec:scripts
---

# Advisory Council Skill

## When to use this skill

Use this skill when the user asks:
- "Run the council" / "运行委员会分析"
- "What should I do to grow my 小红书?" / "小红书怎么增长?"
- "Give me a business review" / "Weekly analysis"
- "What are the top recommendations this week?"
- "Tell me more about recommendation #N" (deeper dive)

## Running the council

```bash
# Full council analysis (all personas in parallel)
python scripts/council.py --run

# Filter to specific source type
python scripts/council.py --run --type rednote

# Deeper dive on recommendation #3
python scripts/council.py --dive 3

# JSON output (for programmatic use)
python scripts/council.py --run --json
```

## Expert personas

The council runs **3 expert personas in parallel**, each seeing only their filtered data slice:

| Persona            | Data slice               | Focus                              |
| ------------------ | ------------------------ | ---------------------------------- |
| GrowthStrategist   | rednote, tiktok          | Follower growth, viral hooks       |
| ContentAnalyst     | rednote, wechat, tiktok  | Content themes, format, language   |
| AudienceInsights   | rednote, twitter, wechat | Audience patterns, engagement cues |

A **Synthesizer** merges findings and ranks by impact.

## Output format

The council outputs a numbered digest:

```
Advisory Council — 小红书 Growth Analysis
[Date]

1. [HIGH] Post personal-story hooks in the first 3 lines — your 3 top performers all do this
2. [MED]  Posting cadence: your data shows Tue/Thu outperform Mon/Fri by 40%
3. [MED]  Trending topic #XX has 2M views; your niche overlaps — create a post this week
4. [LOW]  Caption length: your top posts average 120-150 chars; recent posts are 80 chars

Type "tell me more about #N" for a deeper dive on any recommendation.
```

## Security rules

- Council reads only from the local knowledge base (no live API calls unless explicitly requested)
- Each expert prompt includes only its filtered data slice — no cross-contamination
- Output is synthesized, never raw stored text
- The synthesizer runs secret-redaction on output before printing
