# AGENTS.md

Guidance for AI agents (and humans) working **on this repository**. For the skill's own
runtime behavior — how answers are computed and presented to end users — see
[`bd-income-tax/SKILL.md`](./bd-income-tax/SKILL.md).

## What this is

A Claude Code **plugin marketplace** shipping one Agent Skill, `bd-income-tax`, which computes
and explains **Bangladesh individual (personal) income tax** under the Income Tax Act 2023 and
the current Finance Act. Scope is individuals only — **not** corporate tax or VAT.

## Layout

```
.claude-plugin/marketplace.json     # marketplace manifest — MUST live here, not the repo root
bd-income-tax/                      # the skill (this folder is what users install)
  .claude-plugin/plugin.json        # plugin manifest (holds the version)
  SKILL.md                          # skill instructions / runtime behavior
  scripts/tax_calc.py               # deterministic calculator — the single source of math
  references/                       # per-year data, 9-step procedure, filing rules, sources
  evals/evals.json                  # end-to-end eval cases
CHANGELOG.md  CONTRIBUTING.md  README.md
.github/workflows/selftest.yml      # CI: runs --selftest + validates manifests
.github/workflows/release.yml       # on release publish: attaches bd-income-tax.zip
```

## Core rules (non-negotiable)

- **All tax math goes through `scripts/tax_calc.py`.** Never hand-calculate; never put
  arithmetic in `SKILL.md` or the references.
- **Year parameters live in the `PARAMS` table** in `tax_calc.py` — a yearly update touches
  one place. No network calls anywhere.
- **Cite every rate/threshold** to `references/sources.md`. Figures not confirmed against the
  gazetted Act are marked **⚠️ unverified** and kept out of the calculator.
- **Answers default to plain language** (see `SKILL.md` §4): bottom line + monthly equivalent,
  a clear *income year → assessment year + law* line, a compact table, a what-if savings
  ladder, and a plain disclaimer. **Match the user's language** (English↔Bangla). The full
  numbered procedure with citations is for professionals or on request.
- **Use neutral example figures** in docs and tests — never real personal data.

## Before committing

1. `python3 bd-income-tax/scripts/tax_calc.py --selftest` must pass.
2. Validate JSON: `.claude-plugin/marketplace.json` and `bd-income-tax/.claude-plugin/plugin.json`.
3. If you change slabs/thresholds/rebate logic, update the canonical self-test case **and** an
   eval case in `evals/evals.json`.

## Versioning & releases

- **Semantic Versioning.** Keep these three in sync on every release: `plugin.json` `version`,
  `marketplace.json` `metadata.version`, and `CHANGELOG.md`.
- **[Conventional Commits](https://www.conventionalcommits.org/)** (`feat`/`fix`/`docs`/
  `chore`/`test`/`ci`/`build`).
- Commits are **authored solely by the maintainer, signed, with no AI co-author trailer**
  (AI assistance is disclosed once in the README/CONTRIBUTING instead).
- Cut a release with a signed tag `vX.Y.Z`, a GitHub Release with named notes, and the skill
  archive attached. Build the archive with:
  ```
  git archive --format=zip --prefix=bd-income-tax/ -o bd-income-tax.zip <tag>:bd-income-tax
  ```
  The `release.yml` workflow attaches it automatically on publish.
- Repo-level docs that don't ship in the plugin (this file, `CLAUDE.md`) **don't** need a
  version bump.

## Install / update (reference)

```
/plugin marketplace add arifulislamat/bd-income-tax-skills
/plugin install bd-income-tax@bd-income-tax-skills
# update later (run one at a time):
/plugin marketplace update bd-income-tax-skills
/plugin update bd-income-tax@bd-income-tax-skills
```
Desktop / Claude.ai: download `bd-income-tax.zip` from the latest release and upload it.

## Disclaimer

Everything here is informational only and **not professional tax advice**. AY 2026-27 figures
stay provisional until the Finance Act 2026 is gazetted.
