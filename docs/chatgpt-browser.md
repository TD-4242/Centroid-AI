# ChatGPT in the browser

> **Unverified:** these steps have not yet been tested end to end in browser ChatGPT
> ([#2](https://github.com/TD-4242/Centroid-AI/issues/2)). Steps as of 2026-10. Each untested
> step is marked *(unverified)*. Please report what happens on #2.

These plugins answer questions about Centroid CNC12, Acorn and ALLIN1DC controls and the TECO F510
drive, citing the official manuals by page. In the browser they work as knowledge plugins: no
Python, Git or compiler is needed.

## What you need

- A ChatGPT account with access to Plugin Creator. Which plans include it: *(unverified)*.
- A web browser.

## Install

1. **Download a plugin zip.** Start with Centroid Acorn or Centroid CNC12 Operation.

   | Plugin | Download |
   | --- | --- |
   | Centroid Acorn | [centroid-acorn.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-acorn.zip) |
   | Centroid CNC12 Operation | [centroid-cnc12-ops.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-cnc12-ops.zip) |
   | Centroid PLC | [centroid-plc.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-plc.zip) |
   | Centroid VCP | [centroid-vcp.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-vcp.zip) |
   | Centroid ALLIN1DC | [centroid-allin1dc.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/centroid-allin1dc.zip) |
   | TECO F510 VFD | [teco-f510.zip](https://github.com/TD-4242/Centroid-AI/releases/latest/download/teco-f510.zip) |

   All files and checksums ([SHA256SUMS.txt](https://github.com/TD-4242/Centroid-AI/releases/latest/download/SHA256SUMS.txt))
   are on the [Releases page](https://github.com/TD-4242/Centroid-AI/releases). If a link above
   doesn't work, use that page.

2. **Open Plugin Creator** in a new chat and attach the zip *(unverified: how Plugin Creator is
   started in the browser)*.

3. **Paste this prompt**, replacing the three `<...>` values from the table below:

   ```
   Create a private plugin from the attached zip. It holds one plugin folder: skills/<name>/SKILL.md
   files, their reference/*.md files, a plugin.json and a SOURCE.txt.
   - Keep every SKILL.md and reference file word for word, including page citations and safety notes.
   - Name: <plugin name>. Display name: <display name>.
   - Use the description from plugin.json. Only if you require a description of 30 characters or
     fewer, use instead: "<short description>", and tell me that you did.
   - The scripts/ folder holds optional local helpers; include it if you can, skip it if you can't,
     and tell me which.
   - Tell me about any file you could not include and any error, word for word.
   ```

   | Plugin name | Display name | Short description |
   | --- | --- | --- |
   | centroid-acorn | Centroid Acorn | Centroid Acorn setup help |
   | centroid-cnc12-ops | Centroid CNC12 Operation | Centroid CNC12 operation help |
   | centroid-plc | Centroid PLC | Centroid PLC programming help |
   | centroid-vcp | Centroid VCP | Centroid VCP customization |
   | centroid-allin1dc | Centroid ALLIN1DC | Centroid ALLIN1DC setup help |
   | teco-f510 | TECO F510 VFD | TECO F510 spindle VFD help |

   The short descriptions are 30 characters or fewer, for the case where Plugin Creator requires
   that *(unverified whether it does)*.

4. **Install the private plugin** Plugin Creator produces *(unverified)*.

5. **Use it.** Start a new conversation, type `@`, choose the plugin and ask a question, for
   example "How do I pair two motors on the Y axis of an Acorn and square the gantry?"
   *(unverified)*.

## Without a compiler or Python

Knowledge answers work in the browser. When an answer needs a manual's exact wording, the plugin
gives you the manual's download link (all links: [docs/manuals.md](manuals.md)) or asks you to
upload the PDF and then reads the cited page from it.

Compile and format (in Centroid PLC) run Centroid's compiler on your own computer. They need
Claude Code or Codex on the computer with CNC12 and do not work in the browser.

## Updating

Download the newer zip from the [Releases page](https://github.com/TD-4242/Centroid-AI/releases).
Ask Plugin Creator to update your existing private plugin from it *(unverified)*, or remove the
plugin and install it again. `SOURCE.txt` inside a zip shows its version and the commit it was
built from.

## Troubleshooting

In every case, please post the exact message on [#2](https://github.com/TD-4242/Centroid-AI/issues/2).

| Symptom | Try |
| --- | --- |
| Plugin Creator rejects the zip | Unzip it and attach the files instead, or attach only the `SKILL.md` and `reference/*.md` files. |
| "Description too long" | Use the short description from the table in step 3. |
| The plugin isn't in the `@` menu | Start a new conversation; check the plugin is installed and turned on. |
| Answers ignore the plugin's references | Pick the plugin with `@` and ask it to read its reference files. |
| A manual won't download | Use the link the plugin gives, download the PDF yourself and upload it to the chat. |

## Other ways to install

ChatGPT desktop app, Claude app, Claude Code and Codex: see [installing.md](installing.md).
