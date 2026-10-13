# Centroid AI

Skills and tools that help AI assistants (Claude Code, Codex and the Claude app) work with Centroid
CNC12 controls: PLC programming, the Virtual Control Panel, CNC12 operation, Acorn and
ALLIN1DC installation, and the TECO F510 spindle drive. Everything is generic - nothing here
is tied to one machine. Not affiliated with Centroid or TECO-Westinghouse.

## Quick install

**Claude Code**

    claude plugin marketplace add TD-4242/Centroid-AI
    claude plugin install centroid-plc@centroid-ai

**Codex**

    codex plugin marketplace add TD-4242/Centroid-AI

then install plugins from the Plugins directory.

**Claude app and Cowork:** add the marketplace from *Customize → Plugins*; see
[Claude app and Cowork](docs/installing.md#claude-app-and-cowork).

**ChatGPT in the browser** (unverified, being piloted): download a plugin zip from
[Releases](https://github.com/TD-4242/Centroid-AI/releases) and follow
[docs/chatgpt-browser.md](docs/chatgpt-browser.md). Desktop app:
[ChatGPT (pilot)](docs/installing.md#chatgpt-pilot). Full steps: [docs/installing.md](docs/installing.md).

## Plugins

| Plugin | What it does | Skills / commands |
| --- | --- | --- |
| [centroid-plc](docs/plugins/centroid-plc.md) | Write, read and debug Centroid CNC12 PLC programs (MPU11/ALLIN1DC and Acorn), and compile-check or format .src files with Centroid's own compiler. | `centroid-plc-programming`, `/centroid-plc:compile`, `/centroid-plc:format` |
| [centroid-vcp](docs/plugins/centroid-vcp.md) | Customize the Centroid CNC12 Virtual Control Panel: buttons, skins, graphics, LED states and PLC-wired actions. | `centroid-vcp` |
| [centroid-cnc12-ops](docs/plugins/centroid-cnc12-ops.md) | Operate Centroid CNC12 Mill and Router software: menus, jogging, part zero, tool offsets, running jobs, and G/M-code, parameter and message lookup. | `centroid-cnc12-mill-ops`, `centroid-cnc12-router-ops` |
| [centroid-acorn](docs/plugins/centroid-acorn.md) | Install, wire, configure and troubleshoot a Centroid Acorn controller, including the Acorn Wizard and axis pairing and squaring. | `centroid-acorn-install` |
| [centroid-allin1dc](docs/plugins/centroid-allin1dc.md) | Install, wire, commission and tune a Centroid ALLIN1DC (MPU11) servo controller. | `centroid-allin1dc-install` |
| [teco-f510](docs/plugins/teco-f510.md) | Set up, wire, tune and troubleshoot a TECO-Westinghouse F510 VFD driving a CNC spindle. | `teco-f510` |

## Official manuals

The skills cite Centroid's and TECO's manuals by page; the PDFs are not included. Skills offer
to download them for you, or get them yourself from [docs/manuals.md](docs/manuals.md).

## Contributing

Skill conventions: [docs/authoring.md](docs/authoring.md). Run the checks before a PR:

    python3 tools/check_marketplace.py && python3 tools/check_skill_links.py && \
    python3 tools/sync_shared.py --check && python3 -m unittest discover -s tools/tests -t .

## License

MIT for the skills, scripts and docs in this repo; see [LICENSE.md](LICENSE.md).
