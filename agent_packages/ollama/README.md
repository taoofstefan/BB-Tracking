# BB-Tracking Ollama Work Packages

These packages are written for M3-heavy implementation. Codex should use them as handoff briefs, not as loose ideas.

Suggested flow:

1. Feed one package README to `ollama run minimax-m3:cloud`.
2. Ask M3 for a concrete patch plan and exact code edits.
3. Apply the patch with minimal Codex-side redesign.
4. Run the package verification checks.
5. Ask M3 to review the actual diff.
6. Commit one package at a time.

Package order:

1. `bbtracking-1-schema-validator`
2. `bbtracking-2-async-analysis-service`
3. `bbtracking-3-annotated-video-download`
4. `bbtracking-4-calibration-workflow`
5. `bbtracking-5-rep-phase-detector`
6. `bbtracking-6-fixture-library`
