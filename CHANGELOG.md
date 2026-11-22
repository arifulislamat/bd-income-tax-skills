# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-11-22

Aligned with the gazetted **Finance Act 2026** (Act No. 96 of 2026, gazetted 30 Jun 2026) and
the NBR Income Tax Guide 2026-27 (published Sep 2026). Several AY 2026-27 results change, so
this is a major version.

### Changed (AY 2026-27 and AY 2027-28 figures)
- **Category thresholds corrected.** Women and age 65+: 425,000 → **450,000**. Third-gender and
  persons with disabilities: 500,000 → **525,000**. Gazetted war-wounded freedom fighters and
  injured July fighters: 525,000 → **550,000**. `[FA-2026]` Schedule 2, Part 1, para Ka.
- **Investment rebate (Section 78) reduced.** Now the lowest of 3% of income, **10%** of
  eligible investment (was 15%), and **BDT 750,000** (was 1,000,000). AY 2025-26 keeps the old
  formula. The DPS cap (120,000) and government-securities cap (500,000) are now confirmed.
- **Tax Day replaced by filing windows.** New `--filing-window` / `--filing-date`: 5% incentive
  (max 25,000) for 1 Jul to 30 Sep; neutral to 31 Dec; additional tax of 2% (min 3,000) for
  Jan to Mar, 5% (min 5,000) for Apr to Jun, 10% (min 5,000) after the assessment year, 15%
  (min 10,000) on a Section 212 notice. Late filing **no longer forfeits the rebate**;
  `--filed-late` now applies to AY 2025-26 only and is rejected for later years.
- **Vehicle advance tax (Section 153)** is credited against income tax only. It no longer
  absorbs the net-wealth surcharge, matching the NBR guide's examples 24 and 25. The advance
  tax table in the references is updated (new bands up to BDT 500,000; microbus 40,000).
- **Turnover tax.** The old "0.25% above BDT 4 crore" floor is replaced for AY 2026-27 onward
  by Section 163(6): 1% of business gross receipts where the tax on business income is lower
  (`--turnover-rate` for the other rates). The attribution method is an approximation and the
  calculator says so in its output.
- **AY 2025-26:** removed the unsupported `july_warrior` threshold (that category starts in
  AY 2026-27).
- Reference files rewritten against the primary sources: `filing.md` (who must file, 46 PSR
  services, IT-10B at BDT 50 lakh, one-page return conditions, amended return within 180
  days), `sources.md` (gazette and NBR guide as primary sources).
- The plain-language savings ladder now bottoms out at the **minimum tax**, not zero.

### Added
- **Guided e-Return filing with a browser tool.** New `references/e-return-browser.md` and a
  `SKILL.md` section: with Claude in Chrome or the Claude desktop app's built-in browser the
  skill fills the return on `etaxnbr.gov.bd` screen by screen from a confirmed filing sheet and
  cross-checks the site's tax against the calculator. The user signs in, pays, and presses the
  final submit; the skill never handles passwords, OTPs, payment or final submission. Falls
  back to a manual walkthrough when no browser tool is available.
- **AY 2028-29, 2029-30 and 2030-31**, legislated in advance by the Finance Act 2026 (higher
  thresholds, new 35% top band), flagged as estimates.
- `--disabled-children` (+50,000 threshold per disabled child or dependant).
- `--dividend` (15% flat from AY 2026-27) and `--precious-metal-gain` (5% flat).
- Calculator output: `status`, `regular_income`, `slab_tax`, `tax_due`, `tax_payable_s173`,
  `filing_window`, `early_filing_incentive`, `late_filing_additional_tax`, `turnover_tax`, and
  a `notes` list of caveats to pass on.
- Self-test grown from 8 cases to 24 (71 checks), 12 of them reproducing worked examples from
  the NBR Income Tax Guides.
- `tools/check_repo.py`: checks version sync across `plugin.json`, `marketplace.json` and
  `CHANGELOG.md`, `SKILL.md` frontmatter and size limits, and every eval case's figures against
  the calculator. CI runs it on Python 3.9 and 3.12; the release workflow also checks that the
  tag matches the version.

### Fixed
- CLI input validation: unknown year/category/location, negative amounts, and flags that do
  not apply to the chosen year now fail with a clear message instead of a traceback or a
  silently wrong result.
- Stale calculator docstring ("four canonical test cases").

## [1.4.0] - 2026-07-10

### Changed
- **AY 2026-27 general tax-free threshold raised Tk 375,000 → Tk 400,000.** Parliament passed
  the Finance Bill 2026 with the threshold amended up from the proposed Tk 375,000 to
  Tk 400,000 for FY2026-27 and FY2027-28 (multi-year schedule: 450,000 for 2028-29/2029-30).
  The calculator, references, and worked examples now use 400,000. `[FA-2026]`
- Re-sourced the FY2026-27 figures to the **enacted Finance Act 2026** rather than the
  Finance Bill: renamed the `[FB-2026]` source key to `[FA-2026]`, added the parliamentary-
  passage sources (Dhaka Tribune, The Daily Star), and removed the "provisional / not yet
  gazetted" hedging across `SKILL.md`, the references, `README.md`, and `AGENTS.md`.

### Fixed
- Canonical self-test and eval figures updated for the new threshold: gross tax on the
  ৳800,000-salary case **15,833 → 13,333**; the 1,147,470 worked example **gross 104,494 →
  99,494, after-rebate 70,070 → 65,070**; the 880,000 AY 2026-27 contrast **60,750 → 57,000**.
  AY 2027-28 mirrors AY 2026-27, so its projection changes to match.

## [1.3.0] - 2026-06-20

### Added
- **Assessment Year 2027-28** support (`--year 2027-28`) for forward-looking "what will I owe
  next year" questions. Legislated by the Finance Ordinance 2025 as a two-year fix mirroring
  AY 2026-27; built from the 2026-27 params via `deepcopy` so they never drift, and flagged as
  an estimate subject to the Finance Act 2027. New `references/ay-2027-28.md`.
- **Gratuity exemption** (`--gratuity`, `--gratuity-unapproved`): exempt up to BDT 2.5 crore
  from a government or NBR-approved fund (Sixth Schedule Part 1, paras 5–6); excess taxable as
  employment income. Non-approved funds conservatively treated as fully taxable.
- **Vehicle advance tax** (`--vehicle-advance-tax`, Section 153): modelled as a *non-refundable*
  minimum-tax-style credit — creditable up to the tax due, excess forfeited — distinct from
  refundable salary TDS (Section 86). New return fields `vehicle_credit_used`,
  `nonrefundable_unused`, `refund`.
- Source keys `[ITA-2023-6Sch]`, `[S86]`, `[S153]`, `[SDTT]`, `[VATax]`, `[bdtaxation]`; four
  new self-test cases (5–8) and four new eval cases.

### Notes
- The Finance Act 2026 was **not yet gazetted** as of 2026-06-20 (still the Finance Bill 2026),
  so `[FB-2026]` framing and the remaining ⚠️ unverified figures are retained pending the
  gazette (expected ~30 Jun 2026).

## [1.2.1] - 2026-06-14

### Added
- `license: MIT` and `metadata` (author, source) in the skill's `SKILL.md` frontmatter, plus a
  `LICENSE` copy inside `skills/bd-income-tax/`, so author and license travel with every install
  (e.g. `npx skills add`, which copies only the skill folder).

## [1.2.0] - 2026-06-14

### Changed
- Restructured to the canonical `skills/bd-income-tax/` layout so the skill is discoverable by
  **skills.sh** (`npx skills add arifulislamat/bd-income-tax-skills`) as well as the Claude Code
  plugin system — from one copy. The plugin manifest moved to `.claude-plugin/plugin.json`, the
  marketplace `source` is now `./`, and the calculator path uses
  `$CLAUDE_PLUGIN_ROOT/skills/bd-income-tax/scripts/tax_calc.py`.

### Added
- `npx skills add` (skills.sh) install command in the README.

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
