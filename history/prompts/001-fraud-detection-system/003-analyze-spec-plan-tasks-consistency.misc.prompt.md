---
id: 003
title: Analyze Spec Plan Tasks Consistency
stage: misc
date: 2026-03-13
surface: agent
model: claude-sonnet-4-5
feature: 001-fraud-detection-system
branch: 001-fraud-detection-system
user: pc
command: /sp.analyze
labels: ["analysis", "consistency", "quality-check", "cross-artifact"]
links:
  spec: specs/001-fraud-detection-system/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-fraud-detection-system/spec.md
 - specs/001-fraud-detection-system/plan.md
 - specs/001-fraud-detection-system/tasks.md
 - .specify/memory/constitution.md
tests:
 - Cross-artifact consistency validation
 - Constitution alignment check
 - Coverage gap detection
---

## Prompt

User invoked `/sp.analyze` command with no additional arguments.

The command performs a read-only cross-artifact consistency analysis across spec.md, plan.md, tasks.md, and constitution.md to identify:
- Duplications
- Ambiguities
- Underspecifications
- Constitution violations
- Coverage gaps
- Inconsistencies

## Response snapshot

Generated a structured analysis report with 12 findings across CRITICAL, HIGH, MEDIUM, and LOW severity levels:

**CRITICAL Findings:**
- F1: plan.md is still an unfilled template with placeholders
- F2: Constitution references CSV logging but implementation uses database

**HIGH Findings:**
- F3: Conflict between constitution's "manual approval" requirement and spec's auto-promotion
- F4: Constitution recommends A/B testing but no tasks implement it
- F5: Drift monitoring principle lacks scheduler task coverage

**Coverage Analysis:**
- 100% FR coverage (15/15 functional requirements have tasks)
- All constitution principles mapped except P3 (logging format mismatch) and P10 (scheduler gap)

**Key Recommendations:**
1. Run `/sp.plan` to fill plan.md
2. Update constitution Section 5.3 to reference database audit logging
3. Resolve auto-promote vs manual approval conflict
4. Add drift scheduler task

## Outcome

- ✅ Impact: Identified 2 CRITICAL blockers (unfilled plan.md, logging format inconsistency) and 3 HIGH issues before implementation
- 🧪 Tests: No tests run (read-only analysis)
- 📁 Files: Read 4 artifacts (spec.md, plan.md, constitution.md, tasks.md), wrote 0 files
- 🔁 Next prompts: Fix plan.md, update constitution logging reference, resolve auto-promotion conflict
- 🧠 Reflection: Analysis successfully caught a major artifact gap (unfilled plan.md) that would have blocked implementation. Constitution alignment check revealed logging format drift between spec and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS (all required artifacts analyzed, findings correctly categorized by severity)
- Prompt variant (if applicable): N/A (command-driven skill)
- Next experiment (smallest change to try): Add automated artifact validation pre-commit hook to catch template placeholders
