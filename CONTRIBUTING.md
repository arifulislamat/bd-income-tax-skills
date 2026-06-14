# Contributing

Thanks for helping improve the Bangladesh income-tax skill. Accuracy matters most here — a
wrong rate or threshold is worse than a missing feature.

## Ground rules

- **Cite every number.** Any new or changed rate, threshold, or rule must carry a source in
  [`bd-income-tax/references/sources.md`](./bd-income-tax/references/sources.md). Prefer the
  gazetted Act, the Finance Act, and NBR circulars over secondary coverage.
- **Keep the math in the calculator.** All arithmetic lives in
  [`bd-income-tax/scripts/tax_calc.py`](./bd-income-tax/scripts/tax_calc.py). Year parameters
  go in the `PARAMS` table so a yearly update touches one place. Never hand-calculate in
  `SKILL.md` or the references.
- **Flag the unverified.** If a figure isn't confirmed against the gazetted Act, mark it
  `⚠️ unverified` and keep it out of the calculator.

## Before you open a PR

1. Run the calculator self-test:
   ```bash
   python3 bd-income-tax/scripts/tax_calc.py --selftest
   ```
2. If you changed slabs/thresholds/rebate logic, add or update a canonical case in the
   self-test and an eval case in `bd-income-tax/evals/evals.json`.
3. Keep `plugin.json`, `marketplace.json`, and `CHANGELOG.md` versions in sync when releasing.

## Commit conventions

This repo uses [Conventional Commits](https://www.conventionalcommits.org/)
(`feat:`, `fix:`, `docs:`, `chore:`, `test:`) and [Semantic Versioning](https://semver.org/).

## A note on AI assistance

This project was authored with AI assistance (Claude Code). That does not lower the bar:
contributions — human or AI-assisted — are held to the same standard of cited, verifiable
figures and passing tests.

## Disclaimer

This project is informational only and is not professional tax advice.
