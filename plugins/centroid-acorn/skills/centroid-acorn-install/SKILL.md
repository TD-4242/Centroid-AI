---
name: centroid-acorn-install
description: "Use when installing, wiring, configuring, commissioning, or troubleshooting a Centroid Acorn CNC controller - kit and board I/O, LEDs, bench test, Windows/CNC12 install and license, cabinet wiring (inputs/outputs, E-stop, step/dir drives, home/limit switches, spindle), every Acorn Wizard page including Custom PLC, software/hardware axis pairing and auto-squaring, motion tuning, backlash, travel limits, and symptom-to-fix troubleshooting. Generic to any Acorn machine. Source: Acorn Installation Manual rev6 and Acorn Axis Pairing and Squaring guide rev19."
---

# Centroid Acorn Install & Commissioning

## When to use / when not

Use this skill for **hardware installation and commissioning** of a Centroid **Acorn** CNC
controller: kit and board I/O, bench testing, CNC12 software install and licensing, cabinet
wiring, every Wizard configuration page, software and hardware axis pairing/squaring, and
final motion tuning and troubleshooting. It is a faithful, generic capture of the official
**Acorn Installation Manual** (rev6 11-9-23) and **Acorn Axis Pairing and Squaring guide**
(rev19 10-27-25) — not specific to any one machine.

**Do not use this skill** for PLC stage-language (`.src`) or macro work -- if the
centroid-plc plugin is installed, see `centroid-plc-programming`; otherwise (PLC Manual, PDF p.13).

For operating the control (menus, jogging, part zero, running jobs) and G/M-code, parameter, or
message lookups, if the centroid-cnc12-ops plugin is installed, use
`centroid-cnc12-router-ops`; otherwise (Router Manual §1.5, p.11).

## Essentials

The Acorn is a step/direction motion controller: 4 axes, 8 digital PLC inputs, 8 digital PLC
outputs, 400kHz maximum pulse rate, and 100 Mb/s Ethernet to the PC (Acorn Install App D,
p.123). The Wizard generates the PLC program from its homing and pairing settings (Pairing
Guide p.39).

Recommended install order (and where each lives below):

1. Bench-test the hardware first, before wiring it into the machine. (`hardware.md`)
2. Install CNC12, import the license, and run the communications stress test.
   (`software-setup.md`)
3. Wire the electrical cabinet. (`wiring.md`)
4. Run every applicable Wizard page, including axis pairing if the machine has a paired axis.
   (`wizard.md`, `axis-pairing.md`)
5. Final motion tuning: motor testing, turns-ratio calibration, backlash, travel limits.
   (`commissioning.md`)
6. Diagnose faults in `troubleshooting.md`.

Cautions that recur throughout:
- Use only a shielded Ethernet cable between the PC and Acorn; an unshielded cable causes
  intermittent PC data-receive errors from electrical noise (Acorn Install §2.2, p.9).
- If a custom PLC program is in use, set Custom PLC before hand-editing it, so the Wizard
  stops overwriting it — see [wizard.md](reference/wizard.md#custom-plc-preference).
- Software axis pairing requires a Pro license; it is not included in the Free version of
  Acorn CNC12 (Acorn Install §6.7, p.81).

## Reference router

| Reference file | Look here when... |
| --- | --- |
| [reference/hardware.md](reference/hardware.md) | You need kit part numbers, board specs (axes/I-O/pulse rate/analog), the DB25 pinout, the I/O map, relay board/power specs, LED meanings, or the bench-test hardware setup |
| [reference/software-setup.md](reference/software-setup.md) | You're configuring Windows, installing CNC12, importing the license file, running the communications stress test, generating a configuration report, or running the spindle bench test |
| [reference/wiring.md](reference/wiring.md) | You're wiring the cabinet: layout, inputs, outputs, the +24VDC jumper, E-stop, axis drives, home/limit switches, the spindle motor, or the spindle encoder |
| [reference/wizard.md](reference/wizard.md) | You need a Wizard page's fields, from drive type and I/O definitions through axis config, homing, spindle setup, touch devices, DB25 mapping, control/Wizard preferences (including Custom PLC), and the lube pump |
| [reference/axis-pairing.md](reference/axis-pairing.md) | You're pairing two axis motors, in software or hardware, or homing/squaring a paired gantry |
| [reference/commissioning.md](reference/commissioning.md) | You're doing final motion tuning: motor testing and direction, coarse/fine Overall Turns Ratio calibration, backlash compensation, or software travel limits |
| [reference/troubleshooting.md](reference/troubleshooting.md) | You have a symptom to diagnose, need the PLC diagnostic screen, or want a support/knowledge-base link |

## Useful resources

See [reference/troubleshooting.md](reference/troubleshooting.md) for the full symptom->fix
table; the top-level links (Acorn Install p.5; App C, p.118):

> The manual gives the knowledge base and video library links as `http://` on p.5 but
> `https://` on App C, p.118; shown below as `https://` (Acorn Install p.5, App C, p.118).

- Acorn knowledge base: https://centroidcncforum.com/viewforum.php?f=63
- Acorn knowledge base video library: https://centroidcncforum.com/viewforum.php?f=61
- All Acorn documentation: https://centroidcncforum.com/viewtopic.php?f=60&t=3397
- Free Centroid Community CNC Support Forum: https://centroidcncforum.com/viewforum.php?f=20
- Centroid CNC Technical Support YouTube channel:
  https://www.youtube.com/user/CentroidSupport/videos
- Martyscncgarage YouTube playlist (Centroid CNC Acorn Playlist): https://tinyurl.com/ascxfev4
- Centroid Acorn product page:
  https://www.centroidcnc.com/centroid_diy/acorn_cnc_controller.html
- Factory Direct Technical Support (purchase):
  https://shopcentroidcnc.com/centroid-factory-direct-11-technical-support/

## Manuals

This skill cites: Acorn Install (Acorn Installation Manual), Pairing Guide (Acorn Axis Pairing and Squaring); its PLC Manual and Router Manual pointers are for manuals this plugin does not fetch. Acorn Install citations are printed pages (PDF page = printed + 1); Pairing Guide citations are printed pages, which equal PDF pages. Exact wording is in the official PDF. When an answer
needs text beyond these references, run `python3 <plugin>/scripts/fetch_manual.py <id>` with `acorn-install` or `pairing-guide`
(`<plugin>` is this plugin's root directory):

- exit 0: it printed the local PDF path — read the cited page with `pdftotext -layout -f <p> -l <p> <path> -`
  if available, or open the PDF.
- exit 4: not downloaded yet. Ask the user in plain words, using the requested manual's title and
  size, e.g. "This is best checked against Centroid's <title> (free PDF, about <sizeMB> MB). Want me to download it to
  `~/.centroid-ai/manuals/`? I can also do this automatically from now on, or never ask
  again." Yes → rerun with `--yes`. "Always" → `python3 <plugin>/scripts/centroid_config.py set manuals.autoDownload always`, then rerun. "Never" → set `never`.
- exit 5: the user chose never to download; answer from the references and give the manual and page.
- exit 1: download failed; give the user the printed URL to download by hand.

Download links for every manual: https://github.com/TD-4242/Centroid-AI/blob/main/docs/manuals.md
