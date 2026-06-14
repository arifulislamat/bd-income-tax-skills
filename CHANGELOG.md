# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [1.1.3] - 2026-06-14

### Changed
- Tax-saving advice now renders as a "what-if" savings ladder table (investment amount → 15%
  rebate → resulting tax) instead of a paragraph, so the effect of investing is easy to scan.

## [1.1.2] - 2026-06-14

### Added
- README "Updating" section with the marketplace/plugin update commands and the desktop
  re-upload step.

### Changed
- Invoke the calculator by its full path (via `$CLAUDE_PLUGIN_ROOT`) instead of `cd`-ing into
  the version-numbered install folder, so the command — and any permission allow-rule — stays
  stable across versions.

## [1.1.1] - 2026-06-14

### Changed
- Use a neutral example salary (৳60,000/month + ৳80,000 bonus) in the worked example,
  README, eval case, and calculator self-test.

## [1.1.0] - 2026-06-14

### Changed
- Answers now lead with a plain-language bottom line anyone can understand (with a monthly
  equivalent), a clear "income year → assessment year + governing law" line, a compact table
  with the key numbers bolded, and a money-saving tip. The full numbered procedure with source
  citations is now shown only for professionals or on request.
- Replies match the user's language (English → English, Bangla → Bangla).

## [1.0.2] - 2026-06-14

### Fixed
- Move the marketplace manifest to `.claude-plugin/marketplace.json` so
  `/plugin marketplace add` works. Claude Code looks for the manifest at that path; with it
  at the repo root the command failed with "Marketplace file not found".

## [1.0.1] - 2026-06-14

### Added
- Release workflow that attaches `bd-income-tax.zip` (the skill folder, `SKILL.md` at the top
  level) to every published release, for claude.ai and desktop apps that expect the skill
  directory zipped rather than the repository root.
- `.gitignore` for build artifacts and local settings.

## [1.0.0] - 2026-06-14

### Added
- GitHub Actions CI that runs the calculator self-test and validates the manifests on push.

### Changed
- Promote to a stable **1.0.0** release: all canonical self-tests and eval cases pass.
  AY 2026-27 figures remain provisional until the Finance Act 2026 is gazetted.

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
