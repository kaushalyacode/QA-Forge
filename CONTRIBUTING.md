# Contributing

## Branch → PR → merge

1. `git checkout main && git pull`
2. `git checkout -b <type>/<short-name>` — types: `feat`, `fix`, `docs`, `ci`, `chore`, `refactor`
3. Commit with [Conventional Commits](https://www.conventionalcommits.org/) messages (`feat(skill): add RTM builder`)
4. Push and open a PR against `main`; describe *what* and *why*, and how it was tested
5. CI must be green; squash or merge, delete the branch
6. Start the next piece of work from an updated `main`

## Local checks

```bash
python -m unittest discover -s skills/qa-forge/tests   # path moves to plugins/qa-forge/... after the plugin conversion
```

## Rules for content

- Keep `SKILL.md` short; put detail in `references/` and load it per phase.
- Scripts are Python 3.9+, **stdlib only**, with `--help`.
- Never commit credentials. MCP configs reference secrets as `${VAR}`.
- Verify MCP package names/flags against the vendor README before changing them.
