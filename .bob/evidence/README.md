# Hackathon Evidence — Bob Session Screenshots

This folder must contain screenshots of IBM Bob 2.0 sessions demonstrating the onBob workflow.

## Required Files

| Filename | What to capture |
|---|---|
| `layer1-bob-session.png` | Bob chat showing Layer 1 scan completing — `pillars.json` and `health.json` written |
| `layer3-bob-session.png` | Bob chat showing Layer 3 trace completing — `execution-cards.json` written with `file:line` entries |
| `demo-bob-session.png` | Full demo run — Bob chat showing all 3 layers completing end-to-end |

## How to Capture

1. Run each layer prompt from the README in IBM Bob 2.0
2. When Bob finishes and prints its summary, take a full-window screenshot
3. Save the screenshot here with the exact filename listed above

## Example Layer 1 Prompt

```
Execute the onBob Layer 1 scan using the skill defined in .bob/commands/scan.md
Target repository: target-repo/
Output directory: onbob-output/
```

*These screenshots are required for hackathon judging.*
