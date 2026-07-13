# How to Update BADASS 2

## First rule

After any tracked source change, regenerate and verify `MAP.md` and `LANDING_PAD.md`.

```bash
python scripts/badass.py generate .
python scripts/badass.py check .
python -m unittest discover -s tests
```

## Procedure

1. Inspect `BADASS.md`, relevant controls, and affected mechanisms.
2. Confirm the repository is current and clean.
3. Make the smallest coherent change.
4. Update tests.
5. Regenerate derived files.
6. Run all checks.
7. Review the complete diff.
8. Commit only after every gate passes.
9. Verify remote state when publication matters.

New files must have one distinct purpose, be declared in `control/system.json`, appear in `MAP.md`, and justify why an existing file cannot hold the content.
