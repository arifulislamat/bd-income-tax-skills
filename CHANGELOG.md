# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-06-14

### Added
- End-to-end eval suite (`evals/evals.json`) covering assessment-year selection, calculator
  use, and figure correctness across six prompts.
- `CONTRIBUTING.md` with accuracy rules and commit conventions.
- Expanded README: install methods, assessment-year caveat, badges, and an AI-assistance note.

## [0.1.0] - 2026-06-14

### Added
- Deterministic income-tax calculator (`scripts/tax_calc.py`) for AY 2026-27 and AY 2025-26,
  with `--selftest` covering the canonical cases.
- Reference data with source citations and the ordered 9-step computation procedure.
- `SKILL.md` defining the Bangladesh individual income-tax Agent Skill.
- Claude Code plugin packaging (`plugin.json`, `marketplace.json`).
