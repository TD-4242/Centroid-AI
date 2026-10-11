# Authoring skills

Conventions for adding or changing skills in this repo.

## Conventions

1. **Generic** - no machine content. Nothing tied to one machine, shop or build.
2. **Sourced** - every fact cites a document and section or page; facts that cannot be cited are dropped.
3. **Field-verified label** - board-agnostic lessons that no manual states carry `Field-verified (CNC12, YYYY-MM)`.
4. **Advisory label** - electrical-safety guidance only is marked `**Advisory (not in the manual):**`.
5. **No dangling pointers** - every link and skill name resolves; `tools/check_skill_links.py` enforces this.
6. **Current state** - no tombstones ("previously", "used to", "REMOVED"); describe what is true now.
7. **Shape** - `SKILL.md` (frontmatter, when to use / not, essentials, reference router, manuals, resources) plus `reference/*.md` of roughly 100-250 lines; index files are exempt.
8. **Paths** - mill `c:\cncm`, router `c:\cncr`.

Comments in scripts are 1-2 lines and only where the code is confusing; rationale goes in the
commit message.

## Cross-plugin references

A skill may name skills in its own plugin freely. A skill in another plugin is named
conditionally with a manual fallback: "if the `centroid-vcp` plugin is installed, use
`centroid-vcp`; otherwise see (VCP Manual p.44)". `check_skill_links.py` resolves names against
the whole repo and requires a manual citation on the same line for cross-plugin names.

## Citing manuals

Cite as `(<Cite as> p.<n>)` using the printed page the skill's readers will see; the offset
converts it to the PDF viewer's page. Keep this table in sync with [manuals.md](manuals.md) and
each plugin's `manuals.json`.

| Cite as | PDF page = cited page + |
| --- | --- |
| PLC Manual | 0 |
| VCP Manual | 0 |
| Mill Manual | 1 |
| Router Manual | 1 |
| Acorn Install | 1 |
| Pairing Guide | 0 |
| ALLIN1DC Install | 0 |
| F510 Manual | 0 |

## Adding a plugin

1. Create `plugins/<name>/` with `skills/<skill>/SKILL.md` (and `reference/`), following the conventions above.
2. Add `plugins/<name>/.claude-plugin/plugin.json`:

   ```json
   {
     "name": "<name>",
     "version": "0.1.0",
     "description": "<description>",
     "author": { "name": "Bill Warner" },
     "homepage": "https://github.com/TD-4242/Centroid-AI",
     "repository": "https://github.com/TD-4242/Centroid-AI",
     "license": "MIT",
     "keywords": ["centroid"]
   }
   ```

3. Add the portable `plugins/<name>/plugin.json` (read by Codex):

   ```json
   {
     "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
     "name": "<name>",
     "version": "0.1.0",
     "description": "<description>",
     "author": { "name": "Bill Warner" },
     "homepage": "https://github.com/TD-4242/Centroid-AI",
     "repository": "https://github.com/TD-4242/Centroid-AI",
     "license": "MIT",
     "keywords": ["centroid"],
     "extensions": {
       "com.openai": {
         "interface": {
           "displayName": "<displayName>",
           "shortDescription": "<description>",
           "category": "Manufacturing"
         }
       }
     }
   }
   ```

4. Append a catalog entry to `plugins` in `.claude-plugin/marketplace.json`:

   ```json
   { "name": "<name>", "source": "./plugins/<name>", "description": "<description>", "category": "manufacturing" }
   ```

   and to `plugins` in `.agents/plugins/marketplace.json`:

   ```json
   { "name": "<name>", "source": { "source": "local", "path": "./plugins/<name>" },
     "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" }, "category": "Manufacturing" }
   ```

5. List every manual the skills cite in `plugins/<name>/manuals.json`:

   ```json
   { "id": "plc-manual", "title": "CNC12 PLC Programming Manual", "citeAs": "PLC Manual",
     "url": "https://www.centroidcnc.com/centroid_diy/downloads/centroid_plc_programming_manual.pdf",
     "file": "centroid_plc_programming_manual.pdf", "expectRev": "rev8 07/24/26",
     "expectPages": 132, "pdfOffset": 0, "sizeMB": 3 }
   ```

   Add a new manual to [manuals.md](manuals.md) and the table above.
6. Each knowledge skill ends with the standard "Manuals" section (copy it from an existing skill).
7. Run `python3 tools/sync_shared.py` to copy the shared helpers (`shared/*.py`) into the plugin's `scripts/`; edit them only under `shared/`.
8. Add `docs/plugins/<name>.md` and a README row.
9. Run the checks:

   ```bash
   python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && \
   python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t .
   ```

## Version bumps

When a plugin changes, bump `version` in both of its manifests (`.claude-plugin/plugin.json` and
`plugin.json`) together; `check_marketplace.py` fails if they differ.
