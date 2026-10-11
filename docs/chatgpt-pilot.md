# ChatGPT pilot checklist

For [issue #2](https://github.com/TD-4242/Centroid-AI/issues/2). Try the centroid-acorn and
centroid-cnc12-ops plugins in ChatGPT and record what happens. Install steps:
[ChatGPT (pilot)](installing.md#chatgpt-pilot). Fill in each result, then paste the page into a
comment on the issue.

ChatGPT version and platform:

## 1. Route 1 installs

Clone the repo, open it in the ChatGPT desktop app, and install both plugins from the Plugins
directory.

Result:

## 2. The plugins appear in the `@` menu

Start a chat and type `@`. Note each plugin's name and description as shown, and whether the
description is cut off.

Result:

## 3. Questions load the right reference

Ask each question in a new chat and note which file under `skills/*/reference/` the answer drew
on.

- centroid-acorn: "How do I pair two motors on the Y axis of an Acorn and square the gantry?"
  Expected: `axis-pairing.md`.
- centroid-cnc12-ops: "In CNC12 Router, how do I set part zero for X and Y?" Expected:
  `part-setup.md` in the router skill.

Result:

## 4. Fallback when Python can't run

Ask something the references don't cover in detail, such as "Show me the exact Acorn
Installation Manual text on the Acorn's E-stop wiring." If ChatGPT can't run Python, the skill
should give the manual's download link or ask you to upload the PDF, not fail silently.

Result:

## 5. Is the 30-character description limit enforced?

`python3 tools/check_marketplace.py --profile chatgpt` lists every description over 30
characters (currently all of them). Note whether ChatGPT rejected, truncated or accepted them.

Result:

## 6. Is route 2 needed?

If route 1 worked, say so and skip this. Otherwise try route 2 from the install page and
describe what Plugin Creator did.

Result:

## Next steps

Post the results on issue #2. Shorten the descriptions only if item 5 shows the limit is
enforced; add another install route only if items 1 and 6 show one is needed.
