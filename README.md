# prabhg-plugins

A personal Claude Code plugin marketplace. One repo, cloned or referenced from every machine, holding the plugins and skills I actually use.

Marketplace name: `prabhg-plugins`. Plugins are addressed as `<plugin>@prabhg-plugins`.

## Install on a new machine

```bash
claude plugin marketplace add prabhg/skills-marketplace
claude plugin install fokus@prabhg-plugins
```

Verify:

```bash
claude plugin list
```

### Zero-command alternative

Sync `~/.claude/settings.json` in dotfiles and the marketplace installs itself on launch:

```json
{
  "extraKnownMarketplaces": {
    "prabhg-plugins": {
      "source": { "source": "github", "repo": "prabhg/skills-marketplace" }
    }
  },
  "enabledPlugins": {
    "fokus@prabhg-plugins": true
  }
}
```

## Contents

| Plugin | Source | What it does |
| --- | --- | --- |
| `fokus` | [prabhg/fokus-skill](https://github.com/prabhg/fokus-skill) | Action-first output shaping: next action first, numbered steps, no tangents, visible progress. |

## Adding a plugin

Two patterns, both live in `.claude-plugin/marketplace.json` under `plugins`.

**1. Reference an external repo** — it keeps updating from upstream. The target repo must be a plugin (contain `.claude-plugin/plugin.json`):

```json
{
  "name": "some-plugin",
  "description": "…",
  "source": { "source": "github", "repo": "owner/repo", "ref": "main" }
}
```

Other source forms the schema accepts: `{"source":"url","url":"https://…"}` (also `git@…`), `{"source":"npm","package":"…"}`, and `{"source":"git-subdir","url":"…","path":"sub/dir"}` for monorepos. `ref` and `sha` pin a version on any of the git forms.

**2. Vendor it here** — for skills of mine, or loose `SKILL.md` repos that aren't plugins. Add it under `plugins/` and point at the directory:

```
plugins/my-skill/
  .claude-plugin/plugin.json      # { "name": "my-skill", "version": "0.1.0", "description": "…" }
  skills/my-skill/SKILL.md
```

```json
{ "name": "my-skill", "description": "…", "source": "./plugins/my-skill" }
```

When vendoring someone else's work, keep their LICENSE and attribution.

After editing, `git push`, then on each machine:

```bash
claude plugin marketplace update prabhg-plugins
```

## Rules that bite

- Plugin names must be unique across **all** enabled marketplaces. Currently also enabled here: `claude-plugins-official`, `thedotmack`. Don't reuse a name from either.
- A `github`/`url` source that has no `.claude-plugin/plugin.json` will not install — vendor it instead (pattern 2).
- Marketplace `name` in the manifest is what plugin references resolve against, not the repo name. Repo is `skills-marketplace`; marketplace is `prabhg-plugins`.
